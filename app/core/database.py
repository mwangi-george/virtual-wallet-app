from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, AsyncEngine
from app.core.config import settings

# Create a database engine
engine: AsyncEngine = create_async_engine(
    url=settings.DATABASE_URL,
    future=True,
    connect_args={"statement_cache_size": 0},
)

# Create a session factory bound to the engine
SessionLocal = async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


# Dependency for fastapi routes
async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session
