from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from src.api.auth import create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

# ⚠️ Exemple simple (à remplacer par une table User plus tard)
FAKE_USER = {
    "username": "admin",
    "password": "admin123"
}

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if (
        form_data.username != FAKE_USER["username"]
        or form_data.password != FAKE_USER["password"]
    ):
        raise HTTPException(status_code=401, detail="Identifiants invalides")

    access_token = create_access_token(data={"sub": form_data.username})
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
