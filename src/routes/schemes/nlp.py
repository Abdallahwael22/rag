from pydantic import BaseModel
from typing import Optional

class PushRequest(BaseModel):
    do_reset: Optional[int] = 0

class SearchRequest(BaseModel):
    """the schema for the search endpoint"""
    text:str
    limit:Optional[int] =5
     