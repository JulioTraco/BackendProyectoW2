from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Request, HTTPException, status

#Config
SECRET_KEY = "cambia-esto-por-algo-muy-secreto-en-produccion"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


#passwords
def hash_password(password: str) -> str:
    """Convierte la contraseña en texto plano a un hash bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compara la contraseña ingresada contra el hash guardado en DB."""
    return pwd_context.verify(plain_password, hashed_password)


# jwt

def create_access_token(data: dict) -> str:
    """
    Crea un JWT con los datos del usuario.
    Expira en ACCESS_TOKEN_EXPIRE_MINUTES minutos.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """
    Decodifica y valida un JWT.
    Lanza HTTPException si el token es inválido o expiró.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )


# token cookie o header

def get_token_from_cookie(request: Request) -> str:
    """Lee el JWT desde la cookie llamada 'access_token'."""
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se encontró la cookie de autenticación"
        )
    return token


def get_token_from_header(request: Request) -> str:
    """
    Lee el JWT desde el header Authorization.
    Formato esperado: 'Bearer <token>'
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Header Authorization ausente o formato incorrecto (usar: Bearer <token>)"
        )
    return auth_header.split(" ")[1]