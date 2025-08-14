from pydantic import BaseModel


class SummaryResponse(BaseModel):
    filename: str
    summary: str

    class Config:
        from_attributes = True
