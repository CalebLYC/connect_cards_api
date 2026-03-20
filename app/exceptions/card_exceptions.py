class CardNotFoundException(Exception):
    def __init__(self, card_uid):
        self.card_uid = card_uid
        self.message = f"Card with UID '{self.card_uid}' not found."
        super().__init__(self.message)


class UnauthorizedAccessException(Exception):
    def __init__(self, user_id, project_id):
        self.user_id = user_id
        self.project_id = project_id
        self.message = (
            f"User '{self.user_id}' is unauthorized for project '{self.project_id}'."
        )
        super().__init__(self.message)


class CardInactiveException(Exception):
    def __init__(self, card_uid):
        self.card_uid = card_uid
        self.message = f"Card with UID '{self.card_uid}' is inactive."
        super().__init__(self.message)


class IdentityNotAssignedException(Exception):
    def __init__(self, card_uid):
        self.card_uid = card_uid
        self.message = f"No identity assigned to card with UID '{self.card_uid}'."
        super().__init__(self.message)


class ProjectNotFoundException(Exception):
    def __init__(self, project_id):
        self.project_id = project_id
        self.message = f"Project '{self.project_id}' not found."
        super().__init__(self.message)


class CardAlreadyActiveException(Exception):
    def __init__(self, card_uid):
        self.card_uid = card_uid
        self.message = f"Card with UID '{self.card_uid}' is already active."
        super().__init__(self.message)


class InvalidActivationCodeException(Exception):
    def __init__(self, card_uid):
        self.card_uid = card_uid
        self.message = f"Invalid activation code for card with UID '{self.card_uid}'."
        super().__init__(self.message)


class ActivationCodeExpiredException(Exception):
    def __init__(self, card_uid):
        self.card_uid = card_uid
        self.message = (
            f"Activation code for card with UID '{self.card_uid}' has expired."
        )
        super().__init__(self.message)


class CardNotActiveException(Exception):
    def __init__(self, card_uid):
        self.card_uid = card_uid
        self.message = f"Card with UID '{self.card_uid}' is not currently active."
        super().__init__(self.message)


class MembershipNotFoundException(Exception):
    def __init__(self, identity_id, organization_id):
        self.identity_id = identity_id
        self.organization_id = organization_id
        self.message = f"Identity '{self.identity_id}' has no membership in organization '{self.organization_id}'."
        super().__init__(self.message)


class MembershipInactiveException(Exception):
    def __init__(self, identity_id, organization_id):
        self.identity_id = identity_id
        self.organization_id = organization_id
        self.message = f"Identity '{self.identity_id}' has an inactive membership in organization '{self.organization_id}'."
        super().__init__(self.message)
