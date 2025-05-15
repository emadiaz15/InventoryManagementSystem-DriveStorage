from fastapi import Header, HTTPException, status
from jose import jwt, JWTError, ExpiredSignatureError
from datetime import datetime
from typing import Optional
from .config import settings

ALGORITHM = "HS256"

def verify_jwt_token(
    authorization: Optional[str] = Header(None, description="Token JWT en formato Bearer")
) -> dict:
    """
    🔐 Valida un token JWT enviado por header estándar `Authorization: Bearer <token>`.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Encabezado Authorization faltante o malformado. Se espera 'Bearer <token>'"
        )

    token = authorization.split(" ", 1)[1]

    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

    exp = payload.get("exp")
    if exp and datetime.utcnow().timestamp() > exp:
        raise HTTPException(status_code=401, detail="Token expirado (manual)")

    return payload

auth_dependency = verify_jwt_token
