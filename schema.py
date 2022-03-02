from typing import Optional
from pydantic import BaseModel

class Query(BaseModel):
    shop_url: str
    api_secret: str