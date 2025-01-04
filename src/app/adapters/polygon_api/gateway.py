import httpx

from app.application.protocols.external_api import ExternalApiGateway


class PolygonGateway(ExternalApiGateway):
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key


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
    ) -> dict:
        url = f"{self.base_url}/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from_ts*1000}/{to_ts*1000}"

        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                params={
                    "adjusted": adjusted,
                    "sort": sort,
                    "limit": limit,
                    "apiKey": self.api_key
                }
            )
            if response.status_code == 200:
                data = response.json()
            else:
                raise Exception("data not parsed from polygon")

        return data


