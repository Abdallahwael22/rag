from fastapi import UploadFile
from .BaseController import BaseController
from models import ResponseSignal
from .ProjectController import ProjectController
import re
import os
class DataController(BaseController):
    def __init__(self):
        super().__init__()
        self.scale=1024*1024 # to convert the max file size from MB to bytes
        
    def validate_file(self,file : UploadFile):
        # check the file uploaded is of allowed type and within the size limit
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False, ResponseSignal.FILE_TYPE_NOT_ALLOWED.value
        if file.size > self.app_settings.FILE_MAX_SIZE * self.scale:
            return False, ResponseSignal.FILE_SIZE_EXCEEDS_LIMIT.value
        return True, ResponseSignal.FILE_VALIDATION_SUCCESS.value
    def generate_unique_filepath(self,orig_fil_ename:str,project_id:str):
        random_file_name=BaseController().generate_random_string()
        # checking if the generated file name already exists in the project directory, if it does we generate a new one until we get a unique file name
        project_path=ProjectController().get_project_path(project_id=project_id)
        cleaned_file_name=self.clean_filename(orig_fil_ename)
        new_file_path=os.path.join(
            project_path,
            random_file_name + "_" + cleaned_file_name
        )
        # we check if the file already exists in the project directory, if it does we generate a new file name until we get a unique one
        while os.path.exists(new_file_path):
            random_file_name=BaseController().generate_random_string()
            new_file_path=os.path.join(
                project_path,
                random_file_name + "_" + cleaned_file_name 
            )
        return new_file_path,random_file_name + "_" + cleaned_file_name
    
    def clean_filename(self,orig_fil_ename:str):
        # remove any special characters from the file name to avoid any issues with the file system
        cleaned_filename=re.sub(r'[^\w.]', '', orig_fil_ename.strip())
        cleaned_filename=cleaned_filename.replace(" ","_") # replace spaces with underscores
        return cleaned_filename
        