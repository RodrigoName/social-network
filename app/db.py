from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.config import settings

# Cria o engine SQLAlchemy assíncrono
# O pool_pre_ping=True ajuda a garantir que as conexões no pool ainda estão ativas
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,  # Defina como False em produção para evitar logs excessivos
    pool_pre_ping=True,
)

# Cria uma fábrica de sessões assíncronas
# expire_on_commit=False é importante para que os objetos não expirem após o commit
# e possam ser usados fora do contexto da sessão que os carregou.
AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Função geradora para injeção de dependência no FastAPI.
    Fornece uma sessão de banco de dados assíncrona e garante que ela seja fechada.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()