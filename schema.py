"""
schema.py — the shape of a finished record. A record that fails this
never reaches books.json.
"""

from typing import Optional

from pydantic import BaseModel, HttpUrl, field_validator


class BookRecord(BaseModel):
    title: str
    product_url: HttpUrl
    price_text: str
    price_gbp: float
    availability_text: str
    rating_text: Optional[str] = None
    description: Optional[str] = None
    source_page: HttpUrl
    fetched_at: str

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("title must not be blank")
        return v

    @field_validator("price_gbp")
    @classmethod
    def price_is_sane(cls, v: float) -> float:
        if v is None or v < 0:
            raise ValueError("price_gbp must be a non-negative number")
        return v
