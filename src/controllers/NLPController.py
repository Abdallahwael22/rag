from .BaseController import BaseController
from models.db_schemes import Project,DataChunk
from typing import List
from stores.llm.LLMEnums import DocumentType
import json
class NLPController(BaseController):
    
    def __init__(self,embedding_client,vectordb_client,generation_client):
        super().__init__()
        self.embedding_client = embedding_client
        self.vectordb_client = vectordb_client
        self.generation_client = generation_client
    
    def create_collection_name(self,project_id: str):
        """
        creates a collection name based on the project_id 
        """
        return f"collection_{project_id}".strip()
    
    def reset_vector_db_collection(self,project:Project):
        """
        resets the vector db collection by deleting it
        """
        collection_name =self.create_collection_name(project_id=project.project_id)
        return self.vectordb_client.delete_collection(collection_name=collection_name)
        
    
    def get_vector_db_collection_info(self,project:Project):
        """
        gets the vector db collection by name
        """
        collection_name =self.create_collection_name(project_id=project.project_id)
         
        collection_info=self.vectordb_client.get_collection_info(collection_name=collection_name)
        return json.loads(json.dumps(collection_info,default=lambda x: x.__dict__))
    
    
    def index_into_vector_db(self,project:Project,chunks:List[DataChunk],
                             
                             chunks_ids:List[int],do_reset:bool=False):
        """
        indexes the embedding vectors into the vector db collection
        """
        collection_name =self.create_collection_name(project_id=project.project_id)
        
        texts=[c.chunk_text for c in chunks]
        
        metadata=[c.chunk_metadata for c in chunks]
        
        vectors=[self.embedding_client.embed_text(text,document_type=DocumentType.DOCUMENT.value) for text in texts]
        
        
        _=self.vectordb_client.create_collection(collection_name=collection_name,
                                                 embedding_size=self.embedding_client.embedding_size,
                                                 do_reset=do_reset)    
        _=self.vectordb_client.insert_many(
            collection_name=collection_name,
            text=texts,
            vectors=vectors,
            metadata=metadata,
            record_ids=chunks_ids
        )
        
        return True
    
    def search_vector_db_collection(self,project:Project,text:str,limit:int=10):
        
        collection_name =self.create_collection_name(project_id=project.project_id)
        
        vector =self.embedding_client.embed_text(text=text,document_type=DocumentType.QUERY.value)
        
        if not vector or len(vector)==0:
            return False
        
        results=self.vectordb_client.search_by_vector(
            collection_name=collection_name,
            vector=vector,
            limit=limit
        )
        
        if not results:
            return False
        return json.loads(json.dumps(results,default=lambda x:x.__dict__))
    