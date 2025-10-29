from fastapi import APIRouter ,Depends,UploadFile
import os
from helpers.confog import get_sttings,Settings
from controllers import DataController

data_router = APIRouter(prefix= '/api/v1/data',
                        tags = ["api_v1" ,"data"])

@data_router.post("/upload/{projrct_id}")

async def upload_data(projrct_id:str  , file :UploadFile,
                      app_sttings:Settings = Depends(get_sttings) ):
    

    is_valid, result_signal  = DataController().validate_upload_file(file = file)
    return result_signal