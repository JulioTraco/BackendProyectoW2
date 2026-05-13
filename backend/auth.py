from datetime import datetime, timedelta
from jose import JWTError, jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import os
from dotenv import load_dotenv

# Carga las variables del archivo .env
load_dotenv()

# Lee los valores del .env
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# Hasher de Argon2
ph = PasswordHasher()


def hash_password(password: str) -> str:
    """Convierte el password en texto plano a un hash seguro con Argon2."""
    return ph.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica que el password ingresado coincida con el hash de Argon2."""
    try:
        return ph.verify(hashed_password, plain_password)
    except VerifyMismatchError:
        return False


def dummy_hash():
    """
    Hasheo dummy para cuando el usuario no existe.
    Evita timing attacks — siempre respondemos en el mismo tiempo.
    """
    ph.hash("dummy_password_para_tiempo_constante")


def create_access_token(data: dict) -> str:
    """Crea un JWT con los datos del usuario y expiración del .env."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    """Decodifica y valida un JWT. Devuelve el payload o None si es inválido."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None