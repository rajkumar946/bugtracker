from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import Settings

# get setting instance
settings = Settings()

# Create async engine
engine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)

# Session maker with AsyncSession
async_session = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

# Dependency to get async DB session
async def get_db() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
