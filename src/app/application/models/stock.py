import inspect
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class ExternalApiResult:
    c: float
    h: float
    l: float
    n: int
    o: float
    t: int
    v: int
    vw: float

    @classmethod
    def from_dict(cls, env):
        return cls(**{
            k: v for k, v in env.items()
            if k in inspect.signature(cls).parameters
        })


@dataclass
class ExternalApiResponse:
    adjusted: bool
    next_url: Optional[str]
    query_count: int
    request_id: str
    results: List[ExternalApiResult]
    results_count: int
    status: str
    ticker: str

    @classmethod
    def from_dict(cls, env):
        return cls(**{
            k: v for k, v in env.items()
            if k in inspect.signature(cls).parameters
        })


@dataclass()
class TickerInfo:
    _id: Optional[str]
    ticker: str
    created_at: int
    updated_at: int
    parsed_at: Optional[int]
    is_new: bool

    @classmethod
    def from_dict(cls, env):
        if env:
            return cls(**{
                k: v for k, v in env.items()
                if k in inspect.signature(cls).parameters
            })




