from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.params import Depends
from fastapi.responses import FileResponse

from app.controllers.auth import (
    # google_auth_controller,
    # otp_controller,
    permission_controller,  # Décommenter cette ligne
    # role_controller,
    auth_controller,
    role_controller,
    user_controller,
)
from app.core.config import Settings
from app.providers.providers import get_settings


# Application Fastapi
app = FastAPI(
    title="Connect Cards",
    description="Backend de Connect Cards: application d'authentification des utilisateurs par carte NFC.",
)

# Origins autorisés
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://share.apidog.com/bfd6eb99-7bd3-4f10-8ff6-ef6b0fd504fb",
]

# Configuration des CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_headers="*",
    allow_methods="*",
)

# Ajout des controllers/routers
app.include_router(auth_controller.router)
app.include_router(user_controller.router)
# app.include_router(otp_controller.router)
app.include_router(role_controller.router)
app.include_router(permission_controller.router)  # Décommenter et ajouter cette ligne


# Endpoint racine
@app.get("/")
async def root(settings: Settings = Depends(get_settings)):
    return {
        "msg": "Bienvenue sur l'API Connect Cards !",
        "documentation": f"{settings.base_url}/docs",
        "description": "Backend de Connect Cards: application d'authentification des utilisateurs par carte NFC.",
        "version": "1.0.0",
    }


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("./favicon.ico")