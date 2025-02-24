from pydantic import BaseModel, Field, ConfigDict


class SearchForm(BaseModel):
    """机票查询表单"""
    departure_city: str = Field(..., description="出发城市名称")
    arrival_city: str = Field(..., description="目的城市名称")
    departure_date: str = Field(..., description="出发日期")


class PlaneInfo(BaseModel):
    """机票信息"""
    airline: str = Field("", description="航空公司")
    aircraft_type: str = Field("", description="机型")
    departure_time: str = Field("", description="出发时间")
    arrival_time: str = Field("", description="到达时间")
    flight_duration: str = Field("", description="飞行时间")
    price: str = Field("", description="价格")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "airline": "四川航空",
                "aircraft_type": "波音787",
                "departure_time": "2025-04-01:09:00",
                "arrival_time": "2025-04-01:12:00",
                "flight_duration": "3h",
                "price": "¥399"
            }
        }
    )
