from fastapi import Header, HTTPException, status
from jose import jwt, JWTError, ExpiredSignatureError
from datetime import datetime
from .config import settings

ALGORITHM = "HS256"

def verify_jwt_token(
    x_api_key: str = Header(..., alias="x-api-key", description="Token JWT generado por el backend Django")
) -> dict:
    """
    Verifica el token JWT enviado en el encabezado `x-api-key`.
    Acepta tokens con o sin prefijo 'Bearer '.
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falta el token JWT en x-api-key"
        )

    if x_api_key.startswith("Bearer "):
        token = x_api_key.split(" ", 1)[1]
    else:
        token = x_api_key

    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

    # Validación de expiración manual opcional (por redundancia)
    exp = payload.get("exp")
    if exp and datetime.utcnow().timestamp() > exp:
        raise HTTPException(status_code=401, detail="Token expirado")

    return payload

# Para usarlo como dependencia: `Depends(auth_dependency)`
auth_dependency = verify_jwt_token
