# auth.py
from fastapi import Header, HTTPException, status
from jose import JWTError, jwt
from datetime import datetime
from .config import settings

ALGORITHM = "HS256"

def verify_jwt_token(authorization: str = Header(..., description="Bearer <token>")) -> dict:
    """
    Verifica el token JWT enviado en el encabezado Authorization
    y retorna el payload validado.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
    token = authorization.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[ALGORITHM])
        exp = payload.get("exp")
        if exp and datetime.utcnow().timestamp() > exp:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expirado")
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")

# Alias para usar de forma más semántica:
auth_dependency = verify_jwt_token
