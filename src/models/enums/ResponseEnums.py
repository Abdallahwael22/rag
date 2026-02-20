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
    
    
    
    