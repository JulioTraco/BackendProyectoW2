from sqlmodel import create_engine, Session, SQLModel

#solo cambia el ORM
DATABASE_URL = "sqlite:///./users.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


def create_db():
    """Crea todas las tablas definidas con SQLModel."""
    SQLModel.metadata.create_all(engine)


def get_db():
    """Dependency: abre una sesión por request y la cierra al terminar."""
    with Session(engine) as session:
        yield session