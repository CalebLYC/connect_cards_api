from pydantic import ConfigDict, EmailStr, Field
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Base class of all app settings and configuration params

    Args:
        BaseSettings (Heritage): Base class for settings management using Pydantic.

    Returns:
        Settings: with all env and config properties
    """

    environment: str = Field(..., alias="ENV")
    app_name: str = Field(..., alias="APP_NAME")
    base_url: str = Field(..., alias="BASE_URL")

    # fallback généraux
    default_db_uri: str = Field(
        ..., json_schema_extra={"env": "DATABASE_URI"}, alias="DATABASE_URI"
    )

    # Paramètres JWT et de token
    jwt_algorithm: str = Field(..., alias="JWT_ALGORITHM")
    jwt_secret_key: str = Field(..., alias="JWT_SECRET_KEY")
    access_token_expire_weeks: int = Field(..., alias="ACCESS_TOKEN_EXPIRE_WEEKS")

    # Paramètre du superadministrateur
    admin_email: str = Field(..., alias="ADMINEMAIL")
    admin_password: str = Field(..., alias="ADMINPASSWORD")

    # Paramètres OTP
    otp_expiry_minutes: int = Field(..., alias="OTP_EXPIRY_MINUTES")
    otp_length: int = Field(..., alias="OTP_LENGTH")
    card_activation_code_expiry_minutes: int = Field(
        default=1440, alias="CARD_ACTIVATION_CODE_EXPIRY_MINUTES"
    )

    # URL du frontend à utiliser pour les redirections
    web_frontend_url: str = Field(..., alias="WEB_FRONTEND_URL")
    frontend_auth_success_redirect_uri: str = Field(
        ..., alias="AUTH_SUCCESS_REDIRECT_URI"
    )

    # Paramètre de la base de données en fonction de l'environnement
    @property
    def database_uri(self) -> str:
        """Returns the database URI based on the environment.

        Returns:
            str: The database URI for the current environment.
        """
        return (
            os.getenv(f"DATABASE_URI_{self.environment.upper()}") or self.default_db_uri
        )

    model_config = ConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8",
        validate_by_name=True,
        extra="allow",
        frozen=True,
    )
