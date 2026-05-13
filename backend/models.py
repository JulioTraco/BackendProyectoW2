from sqlmodel import SQLModel, Field
from typing import Optional


class User(SQLModel, table=True):
    """
    SQLModel unifica el modelo de DB y el schema de Pydantic en una sola clase.
    table=True le dice que esta clase representa una tabla en la DB.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    userName: str = Field(unique=True, index=True)
    name: str
    password: str  # siempre guardamos el hash, nunca texto plano