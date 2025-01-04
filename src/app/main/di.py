import os
from functools import partial
from logging import getLogger
from typing import Iterable, Callable

from fastapi import FastAPI, Depends
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorClientSession, AsyncIOMotorDatabase

from app.adapters.motor_mongodb.gateway import MotorGateway
from app.adapters.polygon_api.gateway import PolygonGateway
from app.application.protocols.database import DatabaseGateway, UoW
from app.api.depends_stub import Stub
from app.application.protocols.external_api import ExternalApiGateway
from app.config.base import Settings

logger = getLogger(__name__)

settings = Settings()


async def new_db_gateway(
        database: AsyncIOMotorDatabase,
        session: AsyncIOMotorClientSession = Depends(Stub(AsyncIOMotorClientSession))
):
    yield MotorGateway(database=database, session=session)


async def new_api_gateway(
        settings: Settings
):
    yield PolygonGateway(settings.POLYGON_BASE_URL, settings.POLYGON_API_KEY)


async def new_uow(session: AsyncIOMotorClientSession = Depends(Stub(AsyncIOMotorClientSession))):
    return session


def create_connection(
        settings: Settings,
):
    if not settings.DATABASE_URI:
        raise ValueError("DB_URI env variable is not set")

    mongo_client = AsyncIOMotorClient(settings.DATABASE_URI)
    database = mongo_client[settings.DATABASE_NAME]

    return mongo_client, database


async def new_session(
        mongo_client: AsyncIOMotorClient
) -> Iterable[AsyncIOMotorClientSession]:
    session = await mongo_client.start_session()

    try:
        async with session.start_transaction():
            yield session
    finally:
        await session.end_session()


class ExcludeFromOpenAPI:
    def __init__(self, dependency: Callable):
        self.dependency = Depends(dependency, use_cache=True)
        self.openapi_exclude = True

    def __call__(self):
        return self.dependency.dependency


def init_dependencies(
        app: FastAPI,
        mongo_client: AsyncIOMotorClient,
        database: AsyncIOMotorDatabase
):
    app.dependency_overrides[Settings] = ExcludeFromOpenAPI(settings)

    app.dependency_overrides[AsyncIOMotorClientSession] = partial(new_session, mongo_client)
    app.dependency_overrides[DatabaseGateway] = partial(new_db_gateway, database)
    app.dependency_overrides[ExternalApiGateway] = partial(new_api_gateway, settings)
    app.dependency_overrides[UoW] = new_uow


async def init_db(
        database: AsyncIOMotorDatabase
):
    await MotorGateway.init_db(database, settings.TTL_EXPIRES)

mongo_client, database = create_connection(settings)
