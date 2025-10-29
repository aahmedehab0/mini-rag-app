from fastapi import APIRouter ,Depends
import os
from helpers.confog import get_sttings,Settings

base_router = APIRouter(prefix= '/api/v1',
                        tags = ["api_v1"])



@base_router.get("/")
async def welcome(app_sttings:Settings = Depends(get_sttings)):

    app_name = app_sttings.APP_NAME
    app_version = app_sttings.APP_VERSION
    return {
        "app_name" : app_name,
        "app_version" : app_version,
    }                