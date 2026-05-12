from pydantic import BaseModel


# endpoint /crear-usuario
class UserCreate(BaseModel):
    userName: str
    name: str
    password: str


# endpoint /login
class UserLogin(BaseModel):
    userName: str
    password: str


# /me
class UserResponse(BaseModel):
    id: int
    userName: str
    name: str

    class Config:
        from_attributes = True  