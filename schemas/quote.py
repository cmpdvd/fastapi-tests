from pydantic import BaseModel


class QuoteBase(BaseModel):
    quote: str | None
    child_name: str | None


class QuoteCreate(QuoteBase):
    pass


class QuoteUpdate(QuoteBase):
    pass


class QuoteRead(QuoteBase):
    id: int
    quote: str | None
    child_name: str | None
