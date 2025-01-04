from .protocols.database import DatabaseGateway
from .protocols.external_api import ExternalApiGateway


async def is_active(
        database: DatabaseGateway,
        ticker: str
):
    result = await database.get_ticker_info(ticker=ticker)

    if result:
        return True

    return False


async def add_active_ticker(
        database: DatabaseGateway,
        ticker: str
):
    await database.add_ticker(ticker)


async def get_stock_data(
        database: DatabaseGateway,
        external_api: ExternalApiGateway,
        ticker: str,
        multiplier: int,
        timespan: str,
        from_ts: int,
        to_ts: int,
        adjusted: bool,
        sort: str,
        limit: int
):
    if await is_active(database, ticker):

        results = await database.get_stock_data(
            ticker=ticker,
            multiplier=multiplier,
            timespan=timespan,
            from_ts=from_ts,
            to_ts=to_ts,
            adjusted=adjusted,
            sort=sort,
            limit=limit
        )

        data = {
            "adjusted": adjusted,
            "next_url": None,
            "query_count": results.get("count")[0].get("total_groups"),
            "results_count": len(results.get("data")),
            "request_id": None,
            "results": results.get("data"),
            "status": "OK",
            "ticker": ticker
        }

    else:
        await add_active_ticker(database, ticker)

        data_obj = await external_api.get_data(
            ticker=ticker,
            multiplier=multiplier,
            timespan=timespan,
            from_ts=from_ts,
            to_ts=to_ts,
            adjusted=adjusted,
            sort=sort,
            limit=limit
        )

        # data = data_obj.__dict__
        data = data_obj

    return data
