from fastapi import FastAPI, Depends, HTTPException, status, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import engine, get_db, Base
from models import User
from schemas import UserCreate, UserLogin, UserResponse
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token   # ← así se llama en auth.py
)

# Crea las tablas en la DB al arrancar la app
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Auth API - Segundo Parcial")

# ——— CORS ———
# Permite que el frontend (en otro puerto) se comunique con este backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500"],  # Puerto del Live Server 
    allow_credentials=True,   
    allow_methods=["*"],
    allow_headers=["*"],
)


# POST /crear-usuario
@app.post("/crear-usuario", response_model=UserResponse, status_code=201)
def crear_usuario(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Registra un nuevo usuario en la base de datos.
    La contraseña se guarda hasheada con bcrypt.
    """
    # Verificar que el userName no esté tomado
    existing = db.query(User).filter(User.userName == user_data.userName).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El userName ya está en uso"
        )

    new_user = User(
        userName=user_data.userName,
        name=user_data.name,
        password=hash_password(user_data.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user



# POST /login
@app.post("/login")
def login(credentials: UserLogin, response: Response, db: Session = Depends(get_db)):
    """
    Autentica al usuario y devuelve un JWT de dos formas:
      1. En el body JSON  → para que el frontend lo use como header Bearer
      2. En una cookie httpOnly → el navegador la manda automáticamente
    """
    user = db.query(User).filter(User.userName == credentials.userName).first()

    if not user or not verify_password(credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )

    token = create_access_token(data={"sub": user.userName})

    # Guardar en cookie httpOnly 
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,       
        samesite="lax",      
        max_age=3600,        
    )

    return {
        "message": "Login exitoso",
        "access_token": token,   
        "token_type": "bearer",
    }


# GET /me  (vía cookie)
@app.get("/me/cookie", response_model=UserResponse)
def get_me_cookie(request: Request, db: Session = Depends(get_db)):
    """
    Devuelve la info del usuario autenticado.
    Lee el token desde la cookie httpOnly.
    """
    token = get_token_from_cookie(request)
    payload = decode_token(token)
    userName = payload.get("sub")

    user = db.query(User).filter(User.userName == userName).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


# GET /me  
@app.get("/me/header", response_model=UserResponse)
def get_me_header(request: Request, db: Session = Depends(get_db)):
    """
    Devuelve la info del usuario autenticado.
    Lee el token desde el header: Authorization: Bearer <token>
    """
    token = get_token_from_header(request)
    payload = decode_token(token)
    userName = payload.get("sub")

    user = db.query(User).filter(User.userName == userName).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


# POST /logout 
@app.post("/logout")
def logout(response: Response):
    """Elimina la cookie de autenticación."""
    response.delete_cookie("access_token")
    return {"message": "Sesión cerrada"}