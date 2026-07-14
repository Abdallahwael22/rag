from pydantic import BaseModel, Field,validator
from bson.objectid import ObjectId
from typing import Optional

class DataChunk(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    chunk_text:str=Field(...,min_length=1)
    chunk_metadata:dict
    chunk_order:int=Field(...,ge=0) # to maintain the order of the chunks in the original file
    chunk_project_id:ObjectId
    chunk_asset_id:ObjectId
    
    
    class Config:
        arbitrary_types_allowed = True
    
    @classmethod
    def get_indexes(cls):
        """
        Get the indexes for the DataChunk collection.
        """
        return[{
            "key":[("chunk_project_id",1)],
            "name":"chunk_project_id_chunk_order_index_1",
            "unique":False
            }]
    