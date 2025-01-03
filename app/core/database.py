from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, AsyncEngine
from app.core.config import settings

# Create a database engine
# The engine is responsible for managing connections to the database.
# It is configured to use the database URL from the settings, disabling statement caching.
engine: AsyncEngine = create_async_engine(
    url=settings.DATABASE_URL,
    future=True,
    connect_args={"statement_cache_size": 0},
)

# Create a session factory bound to the engine
# The session factory is used to generate sessions for database transactions.
# It ensures that auto-flush is disabled and that changes are not automatically expired upon commit.
SessionLocal = async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


# Dependency for FastAPI routes
async def get_db() -> AsyncSession:
    """
    This function provides a session to interact with the database for each request.
    The session is automatically closed after use, ensuring proper resource management.
    """
    async with SessionLocal() as session:
        yield session
