import datetime
from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists

from app.core.jwt import JWTUtils
from app.providers.providers import get_db, get_settings
from app.providers.service_providers import get_user_service
from app.repositories.access_token_repository import AccessTokenRepository
from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.models.access_token import AccessToken
from app.providers.repository_providers import (
    get_access_token_repository,
    get_user_repository,
)
from app.services.auth.user_service import UserService
from app.models.project import Project
from app.models.reader import Reader
from app.models.card import Card
from app.models.identity import Identity
from app.models.membership import Membership
from app.models.event import Event
from app.models.webhook import Webhook
from app.models.card_assignment_history import CardAssignmentHistory
from app.models.identity_project_permission import IdentityProjectPermission


oauth_2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def verify_token(
    token: str = Depends(oauth_2_scheme),
    access_token_repos: AccessTokenRepository = Depends(get_access_token_repository),
) -> AccessToken:
    """Verify a token and fetch the associated User with context in one query."""
    try:
        db_token = await access_token_repos.find_by_token(token=token)
        if not db_token or db_token.revoked:
            raise HTTPException(status_code=401, detail="Invalid or revoked token")

        if db_token.expires_at and db_token.expires_at.replace(
            tzinfo=None
        ) < datetime.datetime.utcnow().replace(tzinfo=None):
            raise HTTPException(status_code=401, detail="Token expired")

        payload = JWTUtils.decode_access_token(token=token)
        if not payload or payload.get("sub") != str(db_token.user_id):
            raise HTTPException(status_code=401, detail="Invalid token payload")

        return db_token
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def auth_middleware(
    db_token: AccessToken = Depends(verify_token),
) -> User:
    """Authentication middleware that reuses the eager-loaded user from verify_token."""
    if not db_token.user:
        raise HTTPException(status_code=401, detail="User not found")
    return db_token.user


async def _verify_organization_access(
    request: Request, user: User, db: AsyncSession, permission_code: str = None
) -> None:
    if user.is_superuser():
        return

    # system admins might have some restrictions but usually they can see everything
    if user.has_role("system_admin") or user.has_role("admin"):
        return

    if not user.organization_id:
        raise HTTPException(
            status_code=403, detail="User is not assigned to an organization."
        )

    # 1. Try to get explicit organization_id from path, query, or body
    explicit_org_id = request.path_params.get("organization_id")
    if not explicit_org_id:
        explicit_org_id = request.query_params.get("organization_id")

    if not explicit_org_id and request.method in ["POST", "PUT", "PATCH"]:
        try:
            body = await request.json()
            if isinstance(body, dict):
                explicit_org_id = body.get("organization_id")
        except Exception:
            pass

    # 2. If a resource ID is in the path, we MUST verify its ownership
    resource_org_id = None
    if permission_code:
        resource_type = permission_code.split(":")[0]
        # Look for {resource_type}_id or 'id' (legacy/fallback) in path parameters
        resource_id = request.path_params.get(
            f"{resource_type}_id"
        ) or request.path_params.get("id")

        if resource_id:
            try:
                if resource_type == "project":
                    stmt = select(Project.organization_id).where(
                        Project.id == resource_id
                    )
                    resource_org_id = await db.scalar(stmt)
                elif resource_type == "reader":
                    stmt = select(Reader.organization_id).where(
                        Reader.id == resource_id
                    )
                    resource_org_id = await db.scalar(stmt)
                elif resource_type == "membership":
                    stmt = select(Membership.organization_id).where(
                        Membership.id == resource_id
                    )
                    resource_org_id = await db.scalar(stmt)
                elif resource_type == "webhook":
                    stmt = select(Webhook.organization_id).where(
                        Webhook.id == resource_id
                    )
                    resource_org_id = await db.scalar(stmt)
                elif resource_type == "card":
                    stmt = select(Card.issuer_organization_id).where(
                        Card.id == resource_id
                    )
                    resource_org_id = await db.scalar(stmt)
                elif resource_type == "user":
                    stmt = select(User.organization_id).where(User.id == resource_id)
                    resource_org_id = await db.scalar(stmt)
                elif resource_type == "identity":
                    # For identity, check if a membership exists for the user's organization
                    stmt = select(
                        exists().where(
                            Membership.identity_id == resource_id,
                            Membership.organization_id == user.organization_id,
                        )
                    )
                    is_member = await db.scalar(stmt)
                    if not is_member:
                        raise HTTPException(
                            status_code=403,
                            detail="Identity does not belong to your organization.",
                        )
                    return  # Direct return as it's verified
                elif resource_type == "event":
                    stmt = (
                        select(Project.organization_id)
                        .join(Event, Event.project_id == Project.id)
                        .where(Event.id == resource_id)
                    )
                    resource_org_id = await db.scalar(stmt)
                elif resource_type == "card_assignment_history":
                    stmt = (
                        select(Card.issuer_organization_id)
                        .join(
                            CardAssignmentHistory,
                            CardAssignmentHistory.card_id == Card.id,
                        )
                        .where(CardAssignmentHistory.id == resource_id)
                    )
                    resource_org_id = await db.scalar(stmt)
                elif resource_type == "identity_project_permission":
                    stmt = (
                        select(Project.organization_id)
                        .join(
                            IdentityProjectPermission,
                            IdentityProjectPermission.project_id == Project.id,
                        )
                        .where(IdentityProjectPermission.id == resource_id)
                    )
                    resource_org_id = await db.scalar(stmt)
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(
                    status_code=403,
                    detail=f"Could not verify resource ownership: {str(e)}",
                )

    # 3. Validation logic
    # If both are present, they MUST match
    if explicit_org_id and resource_org_id:
        if str(explicit_org_id) != str(resource_org_id):
            raise HTTPException(
                status_code=403,
                detail="Organization ID mismatch in request parameters.",
            )

    # The effective organization ID is the resource's one if available, otherwise the explicit one
    target_org_id = resource_org_id or explicit_org_id

    if target_org_id and str(user.organization_id) != str(target_org_id):
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to perform operations on this organization.",
        )

    if not target_org_id and not user.has_role("admin"):
        raise HTTPException(
            status_code=403,
            detail="organization_id is required or could not be determined for this operation.",
        )


def require_permission(permission_code: str, verify_org: bool = True) -> Depends:
    try:

        async def dependency(
            request: Request,
            user: User = Depends(auth_middleware),
            ps: UserService = Depends(get_user_service),
            db: AsyncSession = Depends(get_db),
        ):
            try:
                if user.is_superuser():
                    return user

                await ps.ensure_permission(
                    user=user,
                    permission_code=permission_code,
                )

                if verify_org:
                    await _verify_organization_access(
                        request, user, db, permission_code
                    )

                return user
            except HTTPException as e:
                raise e
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error ensuring permission: {str(e)}",
                )

        return Depends(dependency)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error while setting permission dependency: {str(e)}",
        )


def require_role(role_name: str, verify_org: bool = False) -> Depends:
    try:

        async def dependency(
            request: Request,
            user: User = Depends(auth_middleware),
            rs: UserService = Depends(get_user_service),
            db: AsyncSession = Depends(get_db),
        ):
            try:
                if user.is_superuser():
                    return user

                await rs.ensure_role(user=user, role_name=role_name)

                if verify_org:
                    await _verify_organization_access(request, user, db)

                return user
            except HTTPException as e:
                raise e
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error ensuring role: {str(e)}",
                )

        return Depends(dependency)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error while setting permission dependency: {str(e)}",
        )
