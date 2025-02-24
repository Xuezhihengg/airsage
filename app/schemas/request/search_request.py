from pydantic import Field
from app.schemas.base import _BaseModel


class SearchRequest(_BaseModel):

    departure_city: str = Field(..., description="出发城市")
    arrival_city: str = Field(..., description="到达城市")
    departure_date: str = Field(..., description="出发日期")
    airlines: list[str] = Field("", description="航空公司选择")
    price_range: tuple[int, int] = Field(..., description="价格区间")
    departure_time: str = Field(..., description="出发时间（早中晚）")
    aircraft_types: str = Field(..., description="机型选择")
