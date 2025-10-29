from fastapi import APIRouter ,Depends,UploadFile,status
from fastapi.responses import JSONResponse
import os
from helpers.confog import get_sttings,Settings
from controllers import DataController,ProjectController


data_router = APIRouter(prefix= '/api/v1/data',
                        tags = ["api_v1" ,"data"])

@data_router.post("/upload/{projrct_id}")

async def upload_data(projrct_id:str  , file :UploadFile,
                      app_sttings:Settings = Depends(get_sttings) ):
    

    is_valid, result_signal  = DataController().validate_upload_file(file = file)
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content = {
                "signal" : result_signal
            }
        )
    project_dir_path = os.path.join(ProjectController.get_project_path(projrct_id))
    