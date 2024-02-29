from datetime import datetime
from typing import Optional

from beanie import Document, Indexed
from pydantic import BaseModel


class Token(BaseModel):
    value: str
    expire: datetime


class Auth(Document):
    name: str
    user_id: Indexed(float)
    token: Token
