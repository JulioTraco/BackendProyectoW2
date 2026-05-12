from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite se guarda en un archivo local llamado usuarios.db
DATABASE_URL = "sqlite:///./usuarios.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Necesario solo para SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency: se inyecta en cada endpoint para obtener una sesión de DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 