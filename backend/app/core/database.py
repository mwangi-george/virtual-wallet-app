from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import settings

# Create a database engine
engine = create_engine(settings.DATABASE_URL)

# Create a session factory bound to the engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
