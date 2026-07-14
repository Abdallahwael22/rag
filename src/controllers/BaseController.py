from helpers.config import settings, get_settings
import os
import random
import string
class BaseController:
    def __init__(self):
        self.app_settings = get_settings()
        self.base_dir = os.path.dirname(os.path.dirname(__file__)) # get the parent directory of the controllers folder
        self.file_dir=os.path.join(self.base_dir,"assets/files") # directory to store the uploaded files

        self.database_dir=os.path.join(self.base_dir,"assets/database") # directory to store the database files
        
    
    def generate_random_string(self,length: int=12):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    
    
    def get_database_path(self,db_name:str):
        """
        Returns the path to the database directory.
        
        and checks if the directory exists, if not it creates it.
        
        """
        db_path = os.path.join(self.database_dir, db_name)
        if not os.path.exists(db_path):
            os.makedirs(db_path)
        
        return db_path