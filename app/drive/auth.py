# auth.py
from fastapi import Header, HTTPException, status
from jose import JWTError, jwt
from datetime import datetime
from .config import settings

ALGORITHM = "HS256"

def verify_jwt_token(
    x_api_key: str = Header(..., alias="x-api-key", description="Token JWT generado por el backend Django")
) -> dict:
    """
    Verifica el token JWT enviado en el encabezado x-api-key
    (lo acepta con o sin prefijo 'Bearer ').
    """
    # Asegurarnos de que siempre empiece con "Bearer "
    bearer = x_api_key if x_api_key.startswith("Bearer ") else f"Bearer {x_api_key}"
    token = bearer.split(" ", 1)[1]

    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[ALGORITHM])
        exp = payload.get("exp")
        if exp and datetime.utcnow().timestamp() > exp:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expirado")
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")

# Alias semántico para usar como dependencia
auth_dependency = verify_jwt_token
