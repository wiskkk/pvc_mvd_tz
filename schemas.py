from pydantic import BaseModel, HttpUrl


class URLsCreate(BaseModel):
    url: HttpUrl


class URls(BaseModel):
    id: int
    url: HttpUrl

    class Config:
        orm_mode = True
