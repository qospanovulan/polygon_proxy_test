from abc import ABC, abstractmethod

from app.application.models import ExternalApiResponse


class ExternalApiGateway(ABC):

    @abstractmethod
    async def get_data(
            self,
            ticker: str,
            multiplier: int,
            timespan: str,
            from_ts: int,
            to_ts: int,
            adjusted: bool,
            sort: str,
            limit: int
    # ) -> ExternalApiResponse:
    ) -> dict:
        raise NotImplementedError

