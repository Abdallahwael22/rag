from .BaseController import BaseController
from fastapi import UploadFile
from models import ResponseSignal
import os
class ProjectController(BaseController):
    def __init__(self):
        super().__init__()
    def get_project_path(self,project_id:str):
        # construct the path to store the files for the given project id
        project_dir=os.path.join(self.file_dir
                                  ,project_id
                                  )
        # create the directory if it doesn't exist
        if not os.path.exists(project_dir):
            os.makedirs(project_dir)
        return project_dir
