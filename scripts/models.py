from pydantic import BaseModel, validator
from datetime import datetime

class StockData(BaseModel):
    symbol: str
    timestamp: datetime
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: int

    @validator("symbol")
    def symbol_upper(cls, v):
        return v.upper()
