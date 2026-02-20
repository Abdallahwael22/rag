from fastapi import FastAPI, APIRouter ,Depends,UploadFile,status
# status is used to return appropriate HTTP status codes in the response
# JSONResponse is used to return custom error messages with appropriate status codes
from fastapi.responses import JSONResponse
import os
from helpers.config import get_settings,settings
from controllers import DataController,ProcessController,ProjectController
from models import ResponseSignal
import aiofiles
import logging
from .schemes.data import ProcessRequest
logger=logging.getLogger("uvicorn.error") # get the default uvicorn logger to log any errors that occur during file upload or processing
data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1","data"])

@data_router.post("/upload/{project_id}")
async def upload_file(project_id:str , file: UploadFile,app_settings: settings = Depends(get_settings)):
    is_valid, message = DataController().validate_file(file=file)
    if not is_valid:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"is_valid": is_valid, "message": message})
    # get the project path to store the file
    project_dir_path=ProjectController().get_project_path(project_id=project_id)
    # get the file uploaded path to store the file
    # we generate a unique file name to avoid any conflicts with existing files in the project directory, we also clean the file name to remove any special characters that might cause issues with the file system
    file_path,file_id=DataController().generate_unique_filepath(orig_fil_ename=file.filename,project_id=project_id)
    # process the file by chuncks
    try:
        async with aiofiles.open(file_path,"wb") as f:
            while chunks := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunks)
        #save the file to the project directory
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": ResponseSignal.FILE_UPLOAD_FAILED.value})
    return JSONResponse(content={"message":ResponseSignal.FILE_SUCCESSFULLY_UPLOADED.value,"file_id":file_id})
@data_router.post("/process/{project_id}")
async def process_endpoint(project_id : str,proceess_request: ProcessRequest):
    file_id=proceess_request.file_id
    # we will intialize the ProcessController with the project id to process the file in the context of the project
    # this will allow us to access the project directory and the file path to process the file and generate the chunks
    process_controller=ProcessController(project_id=project_id)
    
    file_content=process_controller.get_file_content(file_id=file_id)
    #to take the chunk size and overlap size from the request body
    # we will use the ProcessRequest model to validate the request body and extract the chunk size and overlap size values
    
    chunk_size=proceess_request.chunk_size
    
    overlap_size=proceess_request.overlap_size
    
    if file_content is None:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, 
                            content={"message": ResponseSignal.PROCESSING_FAILED.value})
    else:
        chunks=process_controller.process_file_content(file_id=file_id,
                                                       file_content=file_content,
                                                       chunk_size=chunk_size,
                                                       overlap_size=overlap_size)
    # we will return the chunks as a response to the client, in a real application 
    if chunks is None or len(chunks)==0:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, 
                            content={"message": ResponseSignal.PROCESSING_FAILED.value})
    else:
        #return JSONResponse(content={"message": ResponseSignal.PROCESSING_SUCCESS.value,"chunks":[{"text":chunk.page_content,"metadata":chunk.metadata} for chunk in chunks]})
        return chunks