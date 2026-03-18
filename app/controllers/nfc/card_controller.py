from fastapi import APIRouter, Depends, Query, Path, status
from typing import List
from app.providers.auth_provider import require_permission
from app.providers.service_providers import get_card_service
from app.schemas.card_schema import (
    CardReadSchema,
    LazyCardReadSchema,
    CardCreateSchema,
    CardUpdateSchema,
)
from app.services.nfc.card_service import CardService
from app.utils.constants import http_status

router = APIRouter(
    prefix="/cards",
    tags=["Cards"],
    # dependencies=[require_permission("card:manage")],
    responses=http_status.router_responses,
)


@router.get("/", response_model=List[CardReadSchema], summary="List cards")
async def list_cards(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    eager: bool = Query(True),
    service: CardService = Depends(get_card_service),
):
    return await service.list_cards(skip=skip, limit=limit, eager=eager)


@router.get("/{id}", response_model=CardReadSchema, summary="Get card by ID")
async def get_card(
    id: str = Path(..., min_length=24, max_length=36),
    eager: bool = Query(True),
    service: CardService = Depends(get_card_service),
):
    return await service.get_card(id, eager=eager)


@router.get("/uid/{uid}", response_model=CardReadSchema, summary="Get card by UID")
async def get_card_by_uid(
    uid: str = Path(...),
    service: CardService = Depends(get_card_service),
):
    return await service.get_card_by_uid(uid)


@router.post(
    "/",
    response_model=LazyCardReadSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create card",
)
async def create_card(
    card_create: CardCreateSchema,
    service: CardService = Depends(get_card_service),
):
    return await service.create_card(card_create)


@router.put("/{id}", response_model=LazyCardReadSchema, summary="Update card")
async def update_card(
    id: str = Path(..., min_length=24, max_length=36),
    card_update: CardUpdateSchema = ...,
    service: CardService = Depends(get_card_service),
):
    return await service.update_card(id, card_update)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete card")
async def delete_card(
    id: str = Path(..., min_length=24, max_length=36),
    service: CardService = Depends(get_card_service),
):
    await service.delete_card(id)
    return {"detail": "Card deleted"}


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT, summary="Delete all cards")
async def delete_all_cards(
    service: CardService = Depends(get_card_service),
):
    await service.delete_all_cards()
    return {"detail": "All cards deleted"}
