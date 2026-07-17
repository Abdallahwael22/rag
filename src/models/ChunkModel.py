from .BaseDataModel import BaseDataModel
from .db_schemes import DataChunk
from .enums.DataBaseEnum import DataBaseEnum
from bson.objectid import ObjectId
from pymongo import InsertOne

class ChunkModel(BaseDataModel):
    def __init__(self, db_client):
        super().__init__(db_client=db_client)
        self.collection=self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]
    
    @classmethod
    async def create_instance(cls,db_client:object):
        """
        Create an instance of ChunkModel and initialize the collection.
        because init_collection is an async function, we need to use await to wait for it to complete before returning the instance.
        but we cannot use await in the constructor, so we create a class method to create an instance of the class and initialize the collection.
        """
        instance = cls(db_client=db_client)
        await instance.init_collection()
        return instance
    

    async def create_chunk(self,chunk:DataChunk):
        result= await self.collection.insert_one(chunk.dict(by_alias=True,exclude_unset=True))
        chunk.chunk_id=result.inserted_id
        return chunk
    
    
    async def get_chunk(self,chunk_id):
        result=await self.collection.find_one({"_id":ObjectId(chunk_id)})
        if result is None:
            return None
        return DataChunk(**result)

#insert many chunks at once
    async def insert_many_chunks(self,chunks:list,batch_size: int=100):
        
        for i in range(0,len(chunks),batch_size):
            
            batch=chunks[i:i+batch_size]
            
            operations=[
                InsertOne(chunk.dict(by_alias=True,exclude_unset=True))
                for chunk in batch                
            ]
            
            result=await self.collection.bulk_write(operations)
        
        return len(chunks)
        
            
    async def delete_chunks_by_project_id(self,project_id:str):
        result=await self.collection.delete_many({
                "chunk_project_id":project_id
            })
        return result.deleted_count
    
    async def get_project_chunks(self,project_id:ObjectId,page_no:int,page_size:int=50):
        records= await self.collection.find({
            "chunk_project_id":project_id
        }).skip((page_no-1)*page_size
                ).limit(page_size).to_list(length=None)
        
        return [DataChunk(**record) for record in records]