from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime

class URLCreate(BaseModel):
    original_url: HttpUrl
    expires_at: Optional[datetime] = None


class URLResponse(BaseModel):
    short_url: str


class URLStatsResponse(BaseModel):
    short_code: str
    original_url: HttpUrl
    click_count: int
    created_at: datetime
    expires_at: Optional[datetime] = None