from dataclasses import dataclass
from typing import Annotated, Optional, List

from fastapi import APIRouter, Depends

from app.application.protocols.database import DatabaseGateway
from app.application.protocols.external_api import ExternalApiGateway
from app.application.stocks import get_stock_data
from app.config.base import Settings

stock_router = APIRouter()


@dataclass
class Result:
    c: float
    h: float
    l: float
    n: int
    o: float
    t: int
    v: int
    vw: float


@dataclass
class Response:
    adjusted: bool
    next_url: Optional[str]
    query_count: int
    results_count: int
    request_id: str
    results: List[Result]
    status: str
    ticker: str


@stock_router.get("/")
async def get_bars(
        database: Annotated[DatabaseGateway, Depends()],
        external_api: Annotated[ExternalApiGateway, Depends()],
        settings: Annotated[Settings, Depends()],
        stocks_ticker: str,
        multiplier: int,
        timespan: str,
        from_ts: int,
        to_ts: int,
        adjusted: bool = True,
        sort: str = "asc",
        limit: int = -1
) -> Response:

    data = await get_stock_data(
        database=database,
        external_api=external_api,
        ticker=stocks_ticker,
        multiplier=multiplier,
        timespan=timespan,
        from_ts=from_ts,
        to_ts=to_ts,
        adjusted=adjusted,
        sort=sort,
        limit=limit
    )


    response = Response(
        adjusted=data.get("adjusted"),
        next_url=data.get("next_url"),
        query_count=data.get("query_count"),
        results_count=data.get("results_count"),
        request_id=data.get("request_id"),
        results=[Result(**result) for result in data.get("results")],
        status=data.get("status"),
        ticker=data.get("ticker")
    )

    return response