from .BaseController import BaseController
from .ProjectController import ProjectController
import os
from langchain_community.document_loaders import TextLoader,PyMuPDFLoader
from models import ProcessingEnums
# from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List
from dataclasses import dataclass

@dataclass
class Document:
    page_content: str
    metadata: dict

class ProcessController(BaseController):
    def __init__(self,project_id:str):
        super().__init__()
        self.project_id=project_id
        self.project_path=ProjectController().get_project_path(project_id=project_id)
    
    def get_file_extension(self,file_id:str):
        return os.path.splitext(file_id)[-1]
    
    def get_file_loader(self,file_id:str):
        file_extension=self.get_file_extension(file_id)
        file_path=os.path.join(
            self.project_path,
            file_id
        )
        if not os.path.exists(file_path):
            return None
        if file_extension==ProcessingEnums.TXT.value:
            return TextLoader(file_path,encoding="utf-8")
        elif file_extension==ProcessingEnums.PDF.value:
            return PyMuPDFLoader(file_path)
        else:
            return None
    def get_file_content(self,file_id:str):
        loader=self.get_file_loader(file_id=file_id)
        if loader is not None:
            return loader.load()
        else:
            return None
    def process_file_content(self,file_id:str,file_content:list,chunk_size:int =100,overlap_size : int =20):
        # we will take the output of text or pdf loader and split it into chunks for effiecent processing and embedding generation,
        
        # we will use the chunk size and chunk overlap to control the size of each chunk and 
        
        # the amount of overlap between chunks to ensure that we capture enough context for each chunk while avoiding excessive redundancy
        
        #text_splitter=RecursiveCharacterTextSplitter(chunk_size=chunk_size,chunk_overlap=overlap_size,length_function=len)
        
        #the text loader returns a list of documents, each document has a page content and metadata
        # we will extract the page content and metadata to create the chunks
        file_content_texts=[doc.page_content for doc in file_content]
        
        file_metadata=[doc.metadata for doc in file_content]
        
        #chunks=text_splitter.create_documents(file_content_texts,metadatas=file_metadata)
        chunks = self.process_simpler_splitter(
            texts=file_content_texts,
            metadatas=file_metadata,
            chunk_size=chunk_size,
        )
        
        return chunks

    
    
    def process_simpler_splitter(self, texts: List[str], metadatas: List[dict], chunk_size: int, splitter_tag: str="\n"):
        
        full_text = " ".join(texts)

        # split by splitter_tag
        lines = [ doc.strip() for doc in full_text.split(splitter_tag) if len(doc.strip()) > 1 ]

        chunks = []
        current_chunk = ""

        for line in lines:
            current_chunk += line + splitter_tag
            if len(current_chunk) >= chunk_size:
                chunks.append(Document(
                    page_content=current_chunk.strip(),
                    metadata={}
                ))

                current_chunk = ""

        if len(current_chunk) >= 0:
            chunks.append(Document(
                page_content=current_chunk.strip(),
                metadata={}
            ))

        return chunks