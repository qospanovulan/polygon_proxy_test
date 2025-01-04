from abc import ABC, abstractmethod
from typing import List

from app.application.models import TickerInfo


class UoW(ABC):
    @abstractmethod
    def commit(self):
        raise NotImplementedError

    @abstractmethod
    def flush(self):
        raise NotImplementedError


class DatabaseGateway(ABC):

    @abstractmethod
    async def get_ticker_info(self, **kwargs) -> List[TickerInfo]:
        raise NotImplementedError

    @abstractmethod
    async def add_ticker(self, ticker: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update_tickers_by_id(self, ids: list, **kwargs):
        raise NotImplementedError

    @abstractmethod
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
        raise NotImplementedError

