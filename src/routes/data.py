from fastapi import FastAPI, APIRouter ,Depends,UploadFile,status,Request
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
from models import ProjectModel,ChunkModel,AssetModel
from models.db_schemes import DataChunk,Asset
from models.enums import AssetTypeEnum
from controllers import NLPController
logger=logging.getLogger("uvicorn.error") # get the default uvicorn logger to log any errors that occur during file upload or processing
data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1","data"])

@data_router.post("/upload/{project_id}")
async def upload_file(request: Request,project_id:int , file: UploadFile,app_settings: settings = Depends(get_settings)):
    project_model=await ProjectModel.create_instance(db_client=request.app.db_client)
    
    # check if the project exists, if not, create it
    project=await project_model.get_project_or_create_one(project_id=project_id)
    
    
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
    asset_model=await AssetModel.create_instance(db_client=request.app.db_client)
    asset_resource=Asset(
        asset_name=file_id,
        asset_project_id=project.project_id,
        asset_type=AssetTypeEnum.FILE.value,
        asset_size=os.path.getsize(file_path)
    )
    asset_record= await asset_model.create_asset(asset=asset_resource)
    return JSONResponse(content={"message": ResponseSignal.FILE_SUCCESSFULLY_UPLOADED.value,"file_id":str(asset_record.asset_id,)
                                 })

@data_router.post("/process/{project_id}")
async def process_endpoint(request: Request,project_id : int,proceess_request: ProcessRequest):
    # we will intialize the ProcessController with the project id to process the file in the context of the project
    # this will allow us to access the project directory and the file path to process the file and generate the chunks
    
    
    
    #to take the chunk size and overlap size from the request body
    # we will use the ProcessRequest model to validate the request body and extract the chunk size and overlap size values
    
    chunk_size=proceess_request.chunk_size
    
    overlap_size=proceess_request.overlap_size
    
    do_reset=proceess_request.do_reset
    
    project_model=await ProjectModel.create_instance(db_client=request.app.db_client)
    
    project=await project_model.get_project_or_create_one(project_id=project_id)
    asset_model=await AssetModel.create_instance(db_client=request.app.db_client)
    
    nlp_controller = NLPController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser,
    )
    
    project_files_ids={}
    
    if proceess_request.file_id:
        asset_record=await asset_model.get_asset_record(asset_project_id=project.project_id,asset_name=proceess_request.file_id)
       
        if asset_record is None:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                  content={"message": ResponseSignal.FILE_ID_ERROR.value,
                                 })
        project_files_ids={asset_record.asset_id:asset_record.asset_name}
    else:
        
        project_assets=await asset_model.get_all_project_assets(asset_project_id=project.project_id,asset_type=AssetTypeEnum.FILE.value)
        project_files_ids={asset.asset_id:asset.asset_name for asset in project_assets}
    
    if len(project_files_ids)==0:
              return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                  content={"message": ResponseSignal.FILE_NOT_FOUND.value,
                                 })
    
    process_controller=ProcessController(project_id=project_id)
    no_of_records=0
    no_of_files=0
    chunk_model=await ChunkModel.create_instance(db_client=request.app.db_client)
    if do_reset==1:
            
            collection_name = nlp_controller.create_collection_name(project_id=project.project_id)
            
            _ = await request.app.vectordb_client.delete_collection(collection_name=collection_name)
            
            deleted_count=await chunk_model.delete_chunks_by_project_id(project_id=project.project_id)
            logger.info(f"Deleted {deleted_count} chunks for project {project_id} due to reset flag being set to True.")
    
    for asset_id,file_id in project_files_ids.items():
        file_content=process_controller.get_file_content(file_id=file_id)
        
        if file_content is None:
            logger.error(f"File content is None for file_id: {file_id}. Skipping processing for this file.")
        else:
            chunks=process_controller.process_file_content(file_id=file_id,
                                                        file_content=file_content,
                                                        chunk_size=chunk_size,
                                                        overlap_size=overlap_size)
        # we will return the chunks as a response to the client, in a real application 
        if chunks is None or len(chunks)==0:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, 
                                content={"message": ResponseSignal.PROCESSING_FAILED.value})
        
        file_chunk_records=[
            DataChunk(
        chunk_text=chunk.page_content,
        chunk_metadata=chunk.metadata,
        chunk_order=i,
        chunk_project_id=project.project_id,
        chunk_asset_id=asset_id           
            )
            for i,chunk in enumerate(chunks)
        ]
        
        # we will insert the chunks into the database using the ChunkModel, 
        # we will also check if the do_reset flag is set to True, if it is, 
        # we will delete all the existing chunks for the project before inserting the new chunks, 
        # this is useful when we want to reprocess a file and replace the existing chunks with the new ones.
        # we applied this logic after checking if the file content is not None and the chunks are not empty.
        
        
        
        
        
        no_of_records+=await chunk_model.insert_many_chunks(file_chunk_records)
        no_of_files+=1
    return JSONResponse(content={"message": ResponseSignal.PROCESSING_SUCCESS.value,
                                 "number_of_chunks": no_of_records,
                                 "processed_files": no_of_files
                                 })