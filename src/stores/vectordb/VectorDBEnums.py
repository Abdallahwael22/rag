from enum import Enum

class VectorDBEnums(Enum):
    QDRANT = "QDRANT"
    MILVUS = "MILVUS"
    PINECONE = "PINECONE"
    WEAVIATE = "WEAVIATE"
    
class DistanceMethodEnums(Enum):
    COSINE = "Cosine"
    EUCLIDEAN = "Euclid"
    DOT = "Dot"