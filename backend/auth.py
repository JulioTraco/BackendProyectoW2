from datetime import datetime, timedelta
from jose import JWTError, jwt
import bcrypt

#Clave secreta para firmar los tokens JWT
SECRET_KEY = "clave-super-secreta-cambiame-en-produccion"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  #1 hora de token


def hash_password(password: str) -> str:
    """Convierte el password en texto plano a un hash seguro."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica que el password ingresado coincida con el hash guardado."""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(data: dict) -> str:
    """
    Crea un JWT con los datos del usuario.
    El token incluye una fecha de expiración automática.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    """
    Decodifica y valida un JWT.
    Devuelve el payload si es válido, None si no lo es.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None