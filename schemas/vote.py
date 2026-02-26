from pydantic import BaseModel, model_validator


class VoteBase(BaseModel):
    quote_id: int
    user_id: int | None = None
    device_id: str | None = None
    vote_period: str

    @model_validator(mode="after")
    def user_or_device(self):
        if (self.user_id is None) == (self.device_id is None):
            raise ValueError("Exactly one of user_id or device_id must be provided")
        return self


class VoteCreate(VoteBase):
    pass


class VoteUpdate(VoteBase):
    pass


class VoteRead(VoteBase):
    id: int
    quote_id: int
    user_id: int | None
    device_id: str | None
    vote_period: str
