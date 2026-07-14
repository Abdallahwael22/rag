from enum import Enum

class ResponseSignal(Enum):
    FILE_TYPE_NOT_ALLOWED = "File type is not allowed."
    FILE_SIZE_EXCEEDS_LIMIT = "File size exceeds the maximum limit."
    FILE_SUCCESSFULLY_UPLOADED = "File successfully uploaded."
    FILE_UPLOADED_FAILED = "Failed to upload the file."
    FILE_VALIDATION_SUCCESS = "File is valid."
    FILE_VALIDATION_FAILED = "File is not valid."
    PROCESSING_FAILED = "Failed to process the file."
    PROCESSING_SUCCESS = "File processed successfully."
    DELETING_CHUNKS_SUCCESS = "Chunks deleted successfully."
    FILE_NOT_FOUND = "File not found."
    FILE_ID_ERROR = "File ID is not valid."
    INSERT_INTO_VECTORDB_ERROR="insert into vectordb error"
    INSERT_INTO_VECTORDB_SUCCESS="insert into vectordb successs"
    VECTORDB_COLLECTION_RETRIEVED="vectordb collection retrieved successfully"
    VECTOR_SEARCH_ERROR="Vector search error"
    VECTOR_SEARCH_SUCCESS="vector search success"
    