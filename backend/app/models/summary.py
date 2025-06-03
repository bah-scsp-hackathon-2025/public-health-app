from pydantic import BaseModel


class SummaryResponse(BaseModel):
    description: str
