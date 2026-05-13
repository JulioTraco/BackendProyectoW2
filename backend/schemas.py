from sqlmodel import SQLModel


# Lo que recibe el endpoint /crear-usuario
class UserCreate(SQLModel):
    userName: str
    name: str
    password: str


# Lo que recibe el endpoint /login
class UserLogin(SQLModel):
    userName: str
    password: str


# Lo que devuelve /users/me (nunca devolvemos el password)
class UserResponse(SQLModel):
    id: int
    userName: str
    name: str
    password: str  # devolvemos el hash como pide el profe