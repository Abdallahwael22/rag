from urllib import response
from typing import List,Union
from ..LLMinterface import LLMInterface
from ..LLMEnums import CohereEnums,DocumentType
import cohere
import logging

class CoHereProvider(LLMInterface):
    def __init__(self,api_key:str,
                 default_input_max_characters:int=1000,
                 default_generation_output_max_characters:int=1000,
                 default_generation_temperature:float=0.1):
        self.api_key = api_key
        self.default_input_max_characters = default_input_max_characters
        self.default_generation_output_max_characters = default_generation_output_max_characters
        self.default_generation_temperature = default_generation_temperature
        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None
        
        self.client = cohere.Client(api_key=self.api_key)
        
        self.enums=CohereEnums
        self.logger = logging.getLogger(__name__)
        
        
        
        
    def set_generative_model(self, model_id: str):
        self.generation_model_id = model_id
        self.logger.info(f"Generative model set to: {model_id}")
    
    def set_embedding_model(self, model_id: str, model_embedding_size:int):
        self.embedding_model_id = model_id
        self.embedding_size = model_embedding_size
        self.logger.info(f"Embedding model set to: {model_id} with size {model_embedding_size}")
    
    
    def process_text(self,text:str):
            return text[:self.default_input_max_characters].strip()
        
        
    def generate_text(self, prompt: str, max_output_tokens: int=None, chat_history: list=[], temperature: float = None):
            
            if not self.client:
                self.logger.error("Cohere client is not initialized.")
                return None
            if self.generation_model_id is None:
                self.logger.error("Generative model is not set.")
                return None
            
            response=self.client.chat(
                model=self.generation_model_id,chat_history=chat_history,message=prompt,
                temperature=temperature if temperature is not None else self.default_generation_temperature,
                max_tokens=max_output_tokens if max_output_tokens is not None else self.default_generation_output_max_characters
                )
            if not response or not response.text:
                self.logger.error("No response from Cohere API.")
                return None
            return response.text
            
    def construct_prompt(self, prompt: str, role: str):
        return {"role": role, "text": self.process_text(prompt)}
        
    def embed_text(self, text:Union[str,List[str]],document_type:str=None):
        if not self.client:
            self.logger.error("Cohere client is not initialized.")
            return None
        if isinstance(text,str):
            text=[text]
        
        if self.embedding_model_id is None:
            self.logger.error("Embedding model is not set.")
            return None
        
        input_type=DocumentType.DOCUMENT.value
        
        if document_type==DocumentType.QUERY.value:
            input_type=DocumentType.QUERY.value
        response=self.client.embed(
            model=self.embedding_model_id,
            texts=[self.process_text(t) for t in text ],
            input_type=input_type,
            embedding_types=["float"]
            )
        # 1. Use identity checks (is None) to bypass Cohere's broken __len__ truthiness check
        if response is None:
            self.logger.error("No response returned from Cohere.")
            return None
            
        # 2. Extract the embeddings safely
        embeddings_obj = getattr(response, "embeddings", None)
        if embeddings_obj is None:
            self.logger.error("No embedding field in Cohere response.")
            return None
            
        float_embeddings = getattr(embeddings_obj, "float", None)
        
        # 3. Since float_embeddings is a standard Python list, it is safe to run len() on it
        if float_embeddings is None or len(float_embeddings) == 0:
            self.logger.error("No float embedding data returned from Cohere.")
            return None
            
        # Return the 1D vector of the first (and only) text we passed in
        return [f for f in float_embeddings]