import os
import ssl
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager

DATABASE_URL = os.getenv('DATABASE_URL').replace('postgresql://', 'postgresql+asyncpg://')
ssl_context = ssl.create_default_context()

async_engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"ssl": ssl_context}
)

AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# async def preload_questions_from_excel(session, filepath):
#     import pandas as pd
#     from .models import Section, QuestionBase, QuestionOptions
#
#     df = pd.read_excel(filepath)
#     # TODO: Parse the DataFrame and insert into Section, QuestionBase, QuestionOptions
#     # Example (pseudo-code):
#     # for row in df.itertuples():
#     #     ... create Section, QuestionBase, QuestionOptions as needed
#     pass


async def app_specific_setup():
    from .core import db
    async with async_engine.begin() as conn:
        await conn.run_sync(db.metadata.create_all)
    # # Preload questions/options from Excel
    # async with AsyncSessionLocal() as session:
    #     await preload_questions_from_excel(session, 'research_questions.xlsx')


def init_async_db(app):
    import asyncio
    with app.app_context():
        asyncio.run(app_specific_setup())

@asynccontextmanager
async def get_async_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
