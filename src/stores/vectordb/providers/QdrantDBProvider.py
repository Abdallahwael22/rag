from ..VectorDBInterface import VectorDBInterface
import logging
from ..VectorDBEnums import DistanceMethodEnums
from qdrant_client import QdrantClient,models
class QdrantDBProvider(VectorDBInterface):
    
    def __init__(self,db_path:str,distance_method:str):
        
        self.client=None
        self.db_path=db_path
        self.distance_method=None
        if distance_method == DistanceMethodEnums.COSINE.value:
            self.distance_method = models.Distance.COSINE
        elif distance_method == DistanceMethodEnums.DOT.value:
            self.distance_method = models.Distance.DOT
        elif distance_method == DistanceMethodEnums.EUCLIDEAN.value:
            self.distance_method = models.Distance.EUCLIDEAN
        
        self.logger=logging.getLogger(__name__)
        

    def connect(self):
        self.client = QdrantClient(path=self.db_path)
        self.logger.info(f"Connected to QdrantDB at {self.db_path}")
        
    def disconnect(self):
        self.client=None
        self.logger.info("Disconnected from QdrantDB")
    def is_collection_existed(self,collection_name:str)->bool:
        return self.client.collection_exists(collection_name=collection_name)
    def list_all_collections(self)->list:
        return self.client.get_collections()
    def get_collection_info(self,collection_name:str)->dict:
        return self.client.get_collection(collection_name=collection_name)
    def delete_collection(self,collection_name:str)->bool:
        if self.is_collection_existed(collection_name):
            return self.client.delete_collection(collection_name=collection_name)
    def create_collection(self,collection_name:str,embedding_size:int,do_reset:bool=False)->bool:
        if do_reset:
            _ =self.delete_collection(collection_name)
        if not self.is_collection_existed(collection_name):
            _= self.client.recreate_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(size=embedding_size, distance=self.distance_method)
            )
            return True
        self.logger.warning(f"Collection {collection_name} already exists.")
        return False
    def insert_one(self,collection_name:str,text:str,vector:list,
                   metadata:dict=None,record_id:str=None):
        if not self.is_collection_existed(collection_name):
            self.logger.error(f"Collection {collection_name} does not exist.")
            return False
        try:
            _= self.client.upload_records(
                collection_name=collection_name,
                records=[models.Record(id=[record_id],vector=vector, payload={"text": text,"metadata":metadata})])
        except Exception as e:
            self.logger.error(f"Error occurred while uploading record to QdrantDB: {e}")
            return False
        return True
    
    def insert_many(self,collection_name:str,text:list,vectors:list,
                    metadata:list=None,record_ids:list=None,batch_size:int=50):
        if not self.is_collection_existed(collection_name):
            self.logger.error(f"Collection {collection_name} does not exist.")
            return False
        if metadata is None:
            metadata = [None] * len(text)
        if record_ids is None:
            record_ids = list(range(0,len(text)))
        
        for i in range(0,len(text),batch_size):
            batch_end=i+batch_size
            batch_text = text[i:batch_end]
            batch_vectors = vectors[i:batch_end]
            batch_metadata = metadata[i:batch_end]
            batch_record_ids=record_ids[i:batch_end]
            
            batch_records =[models.Record(id=batch_record_ids[x],vector=batch_vectors[x],payload={"text": batch_text[x],"metadata":batch_metadata[x]})
                            for x in range(len(batch_text))]
            
            try:
                _= self.client.upload_records(
                    collection_name=collection_name,
                    records=batch_records
                )
            except Exception as e:
                self.logger.error(f"Error occurred while uploading records to QdrantDB: {e}")
                return False
        return True   
        
    def search_by_vector(self,collection_name:str,vector:list,limit:int=5):
            if not self.is_collection_existed(collection_name):
                self.logger.error(f"Collection {collection_name} does not exist.")
                return []
            try:
                search_result = self.client.search(
                    collection_name=collection_name,
                    query_vector=vector,
                    limit=limit
                )
                return search_result
            except Exception as e:
                self.logger.error(f"Error occurred while searching in QdrantDB: {e}")
                return []