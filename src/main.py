from fastapi import FastAPI 
from routes import base , data
from motor.motor_asyncio import AsyncIOMotorClient
from helpers import get_setings
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_setings()
    app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)  #define clent
    app.db_client = app.mongo_conn [settings.MONGODB_DATABASE]  #define database
    yield
    app.mongo_conn.close()


app = FastAPI(lifespan=lifespan )


app.include_router(base.base_router)
app.include_router (data.data_router)


#uvicorn main:app --reload  --host 0.0.0.0 --port 5000
# run fastapi from main.py decoder app with reload (refresh directly)
#  any one can access run on port 5000