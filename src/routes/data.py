from fastapi import  APIRouter, Depends, UploadFile, status ,Request
from fastapi.responses import JSONResponse
import aiofiles
import logging
import os

from helpers.confog import get_setings ,Settings
from controllers import DataController,ProcessController
from schemes import ProcessRequest

from models.enums import ResponseSignal , AssetTypeEnum
from models.db_schemes import DataChunk , Asset
from models import ProjectModel ,ChunkModel , AssetModel



logger = logging.getLogger('uvicorn.error')

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1", "data"],
)

@data_router.post("/upload/{project_id}")
async def upload_data(request :Request ,  project_id: str, file: UploadFile,
                      app_settings: Settings = Depends(get_setings)):
        
    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )
    project = await project_model.get_project_or_create_one(
        project_id = project_id
        )
    
    # validate the file properties
    data_controller = DataController()

    is_valid, result_signal = data_controller.validate_uploaded_file(file=file)

    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": result_signal
            }
        )

    file_path, file_id = data_controller.generate_unique_filepath(
        orig_file_name=file.filename,
        project_id=project_id
    )

    try:
        async with aiofiles.open(file_path, "wb") as f:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)
    except Exception as e:

        logger.error(f"Error while uploading file: {e}")

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.FILE_UPLOAD_FAILED.value
            }
        )

    #store asset into data base
    asset_model = await AssetModel.create_instance(
    db_client=request.app.db_client
    )   
    #intilazize files in database
    asset_resource = Asset(
        asset_project_id = project.id,
        asset_type = AssetTypeEnum.FILE.value,
        asset_name = file_id,
        asset_size = os.path.getsize(file_path),
    )
    asset_record = await asset_model.create_assest(asset = asset_resource)


    return JSONResponse(
            content={
                "signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
                "file_id": str (asset_record.id)
            }
        )

@data_router.post("/procrss/{project_id}")

async def process_endpoint (request :Request , project_id: str , process_request :ProcessRequest ):

    file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset

    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )
    project = await project_model.get_project_or_create_one(
        project_id = project_id
        )

    process_controller = ProcessController(project_id = project_id)

    file_content = process_controller.get_file_content (file_id = file_id)

    file_chuncks = process_controller.process_file_content( file_contents =file_content,
                                                       file_id = file_id,
                                                       chunk_size = chunk_size,
                                                       overlap_size =overlap_size )
    
    if file_chuncks is None or len (file_chuncks) ==0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.PROCESSING_FAILED.value
            }
        )
    file_chunks_recordes = [

        DataChunk(
            chunk_text= chunk.page_content,
            chunk_metadata = chunk.metadata,
            chunk_order = i+1,
            chunk_project_id= project.id,
        )
        for i , chunk in  enumerate (file_chuncks)
    ]

    chunk_model = await ChunkModel.create_instance (
        db_client= request.app.db_client 
    )
    
    if do_reset == 1:
        _ = await chunk_model.delete_chunks_by_project_id( 
            project_id=project.id
        )


    no_records  = await chunk_model.insert_chunks(chunks=file_chunks_recordes)

    return  JSONResponse(
        content={
            "signal": ResponseSignal.PROCESSING_SUCCESS.value,
            "inserted_chunks": no_records
        }
    )




