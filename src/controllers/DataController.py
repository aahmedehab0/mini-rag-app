from .BaseController import BaseController
from fastapi import UploadFile
from models import ResponseSignal


class DataController(BaseController):
    def __init__(self):
        super().__init__()
        self.size_scale = 1048576

    def validate_upload_file(self , file :UploadFile):

        if file.content_type not in self.app_Settings.FILE_ALLOWED_TYPES:
            return False , ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value

        elif file.size > self.app_Settings.FILE_MAX_SIZE * self.size_scale:
            return False ,ResponseSignal.FILE_SIZE_EXCEEDED.value
        
        else:
            return True , ResponseSignal.FILE_UPLOAD_SUCCESS.value

