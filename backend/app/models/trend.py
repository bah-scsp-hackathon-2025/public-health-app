from pydantic import BaseModel


class TrendResponse(BaseModel):
    data: dict
