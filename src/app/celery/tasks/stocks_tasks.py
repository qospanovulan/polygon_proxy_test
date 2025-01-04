import time

from asgiref.sync import async_to_sync

from app.celery.celery_app import celery_app, api_gateway, db


async def get_new_tickers():
    new_tickers = await db.get_ticker_info(is_new=True)

    ids = [ticker._id for ticker in list(filter(lambda x: x.is_new, new_tickers))]

    await db.update_tickers_by_id(
        ids=ids,
        is_new=False
    )
    return new_tickers


async def parse_stock_data():

    tickers = await get_new_tickers()

    for ticker_info in tickers:
        to_time = int(time.time())
        if ticker_info.is_new:
            from_time = to_time - 30 * 24 * 60 * 60
        else:
            from_time = ticker_info.parsed_at


        data = await api_gateway.get_data(
            ticker=ticker_info.ticker,
            multiplier=1,
            timespan="second",
            from_ts=from_time,
            to_ts=to_time,
            adjusted=True,
            sort="asc",
            limit=-1
        )

        await db.add_stock_data(
            ticker=ticker_info.ticker,
            stock_data=data.get("results")
        )

        await db.update_tickers_by_id(
            ids=[ticker_info._id],
            parsed_at=to_time
        )



@celery_app.task
def parse_stock_data_task(
        task_name: str
):
    """
    1. Getting active tickers from active_tickers collection
    2. Getting data for last 30 days for every minute for the first time parsing.
    3. If not first time, then parsing only last minutes
    4. Storing data in stock_data collection
    """
    try:
        result = async_to_sync(parse_stock_data)()
    except Exception as e:
        return None

    return result




