from pydantic import Field
from app.schemas.base import _BaseModel


class SearchRespones(_BaseModel):

    id: str = Field(..., description="查询ID")
    airline: str = Field(..., description="航空公司")
    flight_number: str = Field(..., description="航班号")
    departure: str = Field("", description="出发城市")
    arrival: str = Field(..., description="到达城市")
    departure_time: str = Field(..., description="出发时间")
    arrival_time: str = Field(..., description="到达时间")
    duration: str = Field(..., description="历时")
    aircraft: str = Field(..., description="机型选择")
    stops: str = Field(..., description="中转次数")