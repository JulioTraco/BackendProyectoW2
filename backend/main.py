from fastapi import FastAPI, Depends, HTTPException, Cookie, Header, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

import models
import schemas
import auth
from database import create_db, get_db

# Crea las tablas al arrancar
create_db()

app = FastAPI(title="Proyecto Parcial 2 - Auth API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# POST /crear-usuario
@app.post("/crear-usuario", response_model=schemas.UserResponse, status_code=201)
def crear_usuario(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """Crea un nuevo usuario con la contraseña hasheada con Argon2."""
    existing = db.exec(select(models.User).where(models.User.userName == user_data.userName)).first()
    if existing:
        raise HTTPException(status_code=400, detail="El userName ya está en uso")

    new_user = models.User(
        userName=user_data.userName,
        name=user_data.name,
        password=auth.hash_password(user_data.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# POST /login  (OAuth2 — recibe form-data)
@app.post("/login")
def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login con OAuth2 (form-data, no JSON).
    - Si las credenciales son incorrectas hace un hasheo dummy para
      responder siempre en el mismo tiempo (evita timing attacks).
    - Si son correctas devuelve el JWT en el body Y lo manda como cookie httpOnly.
    """
    user = db.exec(select(models.User).where(models.User.userName == form_data.username)).first()

    if not user:
        auth.dummy_hash()  # tiempo constante aunque el usuario no exista
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    if not auth.verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    token = auth.create_access_token(data={"sub": user.userName})

    # Cookie httpOnly, el navegador la manda automáticamente, JS no puede leerla
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=180  #3 minutos en segundos
    )

    return {
        "message": "Login exitoso",
        "access_token": token,
        "token_type": "bearer"
    }


# GET /users/me  (cookie O header)
@app.get("/users/me", response_model=schemas.UserResponse)
def get_me(
    db: Session = Depends(get_db),
    access_token: str | None = Cookie(default=None),
    authorization: str | None = Header(default=None)
):
    """
    Devuelve info del usuario autenticado.
    Acepta el token desde cookie httpOnly O desde header Authorization: Bearer.
    """
    token = None

    if access_token:
        token = access_token
    elif authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]

    if not token:
        raise HTTPException(status_code=401, detail="No se proporcionó token de autenticación")

    payload = auth.decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    userName = payload.get("sub")
    user = db.exec(select(models.User).where(models.User.userName == userName)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return user