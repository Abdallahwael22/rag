from .BaseDataModel import BaseDataModel
from .enums.DataBaseEnum import DataBaseEnum
from .db_schemes import Asset
from bson.objectid import ObjectId
class AssetModel(BaseDataModel):
    def __init__(self,db_client:object):
        super().__init__(db_client=db_client)
        self.collection=self.db_client[DataBaseEnum.COLLECTION_ASSET_NAME.value]
    @classmethod
    async def create_instance(cls,db_client:object):
        """
        Create an instance of AssetModel and initialize the collection.
        because init_collection is an async function, we need to use await to wait for it to complete before returning the instance.
        but we cannot use await in the constructor, so we create a class method to create an instance of the class and initialize the collection.
        the index
        """
        instance = cls(db_client=db_client)
        await instance.init_collection()
        return instance
    
    
    
    
    async def get_all_project_assets(self,asset_project_id : str,asset_type : str):
        """
        Get all assets for a specific project.
        """
        record= await self.collection.find({"asset_project_id":ObjectId(asset_project_id)
                                     if  isinstance(asset_project_id,str) else asset_project_id,
                                     "asset_type": asset_type}
                                    ).to_list(length=None)
        return [Asset(**asset) for asset in record]

    async def get_asset_record(self,asset_project_id : str,asset_name: str):
        """
        Get a specific asset record for a project by asset name.
        """
        record= await self.collection.find_one({"asset_project_id":ObjectId(asset_project_id)
                                     if  isinstance(asset_project_id,str) else asset_project_id,
                                     "asset_name": asset_name}
                                    )
        if record:
            return Asset(**record)
        return None