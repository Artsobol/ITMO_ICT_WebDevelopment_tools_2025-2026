from pydantic import BaseModel, HttpUrl


class ParseRequest(BaseModel):
    url: HttpUrl


class ParseResponse(BaseModel):
    message: str
    title: str
    genre: str
    created: bool
