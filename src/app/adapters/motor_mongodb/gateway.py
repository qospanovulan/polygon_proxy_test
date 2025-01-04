import time
from typing import List

from pymongo import UpdateOne
from pymongo.errors import OperationFailure

from app.application.models import TickerInfo
from app.application.protocols.database import DatabaseGateway
from motor.motor_asyncio import AsyncIOMotorClientSession, AsyncIOMotorDatabase


class MotorGateway(DatabaseGateway):
    def __init__(self, database: AsyncIOMotorDatabase, session: AsyncIOMotorClientSession | None):
        self.database = database
        self.session = session

    @classmethod
    async def init_db(cls, db: AsyncIOMotorDatabase, ttl_index_expire_time: int):
        try:
            await db.create_collection('stock_data')
        except Exception as e:
            pass

        try:
            await db.create_collection('active_tickers')
        except Exception as e:
            pass

        await db['stock_data'].create_index(
            [('ticker', 1), ('t', 1)],
            unique=True
        )

        try:
            await db['stock_data'].create_index(
                [('t', 1)],
                expireAfterSeconds= ttl_index_expire_time
            )
        except Exception as e:  # if expires time changed
            await db['stock_data'].drop_index('t_1')
            await db['stock_data'].create_index(
                [('t', 1)],
                expireAfterSeconds=ttl_index_expire_time
            )


    async def get_ticker_info(self, **kwargs) -> List[TickerInfo]:
        collection = self.database['active_tickers']

        tickers = await collection.find(
            kwargs,
            session=self.session).to_list()

        return [TickerInfo.from_dict(ticker) for ticker in tickers]

    async def add_ticker(self, ticker: str):
        collection = self.database['active_tickers']

        current_timestamp = int(time.time())

        result = await collection.insert_one({
            "ticker": ticker,
            "is_new": True,
            "created_at": current_timestamp,
            "updated_at": current_timestamp,
            "parsed_at": None
        }, session=self.session)

        return

    async def update_tickers_by_id(self, ids: list, **kwargs):
        collection = self.database['active_tickers']

        await collection.update_many(
            {"_id": {"$in": ids}},
            {"$set": kwargs}
        )

    async def get_stock_data(
            self,
            ticker: str,
            multiplier: int,
            timespan: str,
            from_ts: int,
            to_ts: int,
            adjusted: bool,
            sort: str,
            limit: int
    ):
        collection = self.database['stock_data']

        seconds = {
            "second": 1,
            "minute": 60,
            "hour": 60 * 60,
            "day": 24 * 60 * 60
        }

        pipeline = [
            {
                "$match": {
                    "ticker": ticker,
                    "t": {
                        "$gte": from_ts,
                        "$lt": to_ts,
                    }
                }
            }, {
                "$project": {
                    "_id": 0,
                    "ticker": 1,
                    "c": 1,
                    "h": 1,
                    "l": 1,
                    "n": 1,
                    "o": 1,
                    "t": 1,
                    "v": 1,
                    "vw": 1,
                    "group_key": {
                        "$subtract": [
                            {"$toLong": "$t"},
                            {"$mod": [{"$toLong": "$t"}, seconds[timespan] * multiplier]}
                        ]
                    }
                }
            }, {
                "$group": {
                    "_id": "$group_key",
                    "c": {"$last": "$c"},
                    "h": {"$max": "$h"},
                    "l": {"$min": "$l"},
                    "n": {"$sum": "$n"},
                    "o": {"$first": "$o"},
                    "t": {"$first": "$t"},
                    "v": {"$sum": 1},
                    "vw": {"$avg": "$vw"},
                }
            },
            {
                "$project": {
                    "_id": 0
                }
            },
            {
                "$facet": {
                    "data": [
                        {"$sort": {"_id": 1 if sort == "asc" else -1}},
                        {"$limit": limit} if limit > 0 else None
                    ],
                    "count": [
                        {"$count": "total_groups"}
                    ]
                }
            }
        ]

        try:
            data = await collection.aggregate(pipeline).to_list()
        except OperationFailure as e:
            raise OperationFailure(f"{e}")

        return data[0]


    async def add_stock_data(
            self,
            ticker,
            stock_data,
    ):

        collection = self.database['stock_data']

        operations = [
            UpdateOne(
                {"ticker": ticker, "t": item['t']},
                {"$setOnInsert": {**item, "ticker": ticker, "t": item['t']//1000}},
                upsert=True
            )
            for item in stock_data
        ]

        result = await collection.bulk_write(operations)
