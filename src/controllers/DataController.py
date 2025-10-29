from .BaseController import BaseController
from fastapi import UploadFile

class DataController(BaseController):
    def __init__(self):
        super().__init__()
        self.size_scale = 1048576

    def validate_upload_file(self , file :UploadFile):

        if file.content_type not in self.app_Settings.FILE_ALLOWED_TYPES:
            return False , "File_type_not_supported"

        elif file.size > self.app_Settings.FILE_MAX_SIZE * self.size_scale:
            return False ,"File_size_exceeded"
        
        else:
            return True , "success"
