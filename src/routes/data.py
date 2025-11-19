from fastapi import  APIRouter, Depends, UploadFile, status ,Request
from fastapi.responses import JSONResponse
import aiofiles
import logging
import os

from helpers.confog import get_setings ,Settings
from controllers import DataController,ProcessController ,NLPController
from .schemes import ProcessRequest

from models.enums import ResponseSignal , AssetTypeEnum
from models.db_schemes import DataChunk , Asset
from models import ProjectModel ,ChunkModel , AssetModel




logger = logging.getLogger('uvicorn.error')

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1", "data"],
)

@data_router.post("/upload/{project_id}")
async def upload_data(request :Request ,  project_id: int, file: UploadFile,
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
        asset_project_id = project.project_id,
        asset_type = AssetTypeEnum.FILE.value,
        asset_name = file_id,
        asset_size = os.path.getsize(file_path),
    )
    asset_record = await asset_model.create_assest(asset = asset_resource)


    return JSONResponse(
            content={
                "signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
                "file_id": str (asset_record.asset_id)
            }
        )

@data_router.post("/process/{project_id}")
async def process_endpoint (request :Request , project_id: int , process_request :ProcessRequest ):
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset

    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )

    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )

    nlp_controller =  NLPController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser,
    )

    asset_model = await AssetModel.create_instance(                 
            db_client=request.app.db_client
        )

    project_files_ids = {}
    if process_request.file_id:                                     #if I pass file id
        asset_record = await asset_model.get_asset_record(
            asset_project_id=project.project_id,
            asset_name=process_request.file_id
        )

        if asset_record is None:                                        ##if Id not founded on DB raise file id error response
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignal.FILE_ID_ERROR.value,
                }
            )

        project_files_ids = {                                           ##if Id founded on DB pass uninue id and asset name to dict
            asset_record.asset_id: asset_record.asset_name                    ##to process it
        }
    
    else:                                                            #if I didn't pass file id
        
        project_files = await asset_model.get_all_project_assets(       ##get folder id from link and get data from DB     
            asset_project_id=project.project_id,
            asset_type=AssetTypeEnum.FILE.value,
        )

        project_files_ids = {                                            ##get all files from db with this id
            record.asset_id: record.asset_name
            for record in project_files
        }

    if len(project_files_ids) == 0:                                   #raise no files if ther's no files in folder
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.NO_FILES_ERROR.value,
            }
        )
    
    process_controller = ProcessController(project_id=project_id)      #get chunks and metadata from files

    no_records = 0
    no_files = 0

    chunk_model = await ChunkModel.create_instance(
                        db_client=request.app.db_client
                    )

    if do_reset == 1:                                                  #if reset= 1 delete all files from project

        collection_name = nlp_controller.create_collection_name(project_id=project.project_id)
        _ = await request.app.vectordb_client.delete_collection(collection_name=collection_name)       

        _ = await chunk_model.delete_chunks_by_project_id(
        project_id=project.project_id
        )

    for asset_id, file_id in project_files_ids.items():                 #loop all files 

        file_content = process_controller.get_file_content(file_id=file_id)

        if file_content is None:                                            ## if no content in file continue
            logger.error(f"Error while processing file: {file_id}")
            continue

        file_chunks = process_controller.process_file_content(               ##process file content in file chunks
            file_contents=file_content,
            file_id=file_id,
            chunk_size=chunk_size,
            overlap_size=overlap_size
        )

        if file_chunks is None or len(file_chunks) == 0:                    ## if no chunks raise raise PROCESSING_FAILED
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignal.PROCESSING_FAILED.value
                }
            )

        file_chunks_records = [                                              ##process chuks
            DataChunk(
                chunk_text=chunk.page_content,
                chunk_metadata=chunk.metadata,
                chunk_order=i+1,
                chunk_project_id=project.project_id,
                chunk_asset_id=asset_id
            )
            for i, chunk in enumerate(file_chunks)
        ]

        no_records += await chunk_model.insert_many_chunks(                       ##add chunks to DB
            chunks=file_chunks_records
            )
        no_files += 1

    return JSONResponse(                                                # return PROCESSING_SUCCESS
        content={
            "signal": ResponseSignal.PROCESSING_SUCCESS.value,
            "inserted_chunks": no_records,
            "processed_files": no_files
        }
    )