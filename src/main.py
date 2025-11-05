from fastapi import FastAPI 
from routes import base , data
from motor.motor_asyncio import AsyncIOMotorClient
from helpers import get_setings
from contextlib import asynccontextmanager
from stores.llm import LLMProviderFactory


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_setings()
    app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)  #define clent
    app.db_client = app.mongo_conn [settings.MONGODB_DATABASE]  #define database

    llm_provider_factory = LLMProviderFactory(settings)        #get configs settings for llm provider

    # generation client
    app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id = settings.GENERATION_MODEL_ID)

    # embedding client
    app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID,
                                             embedding_size=settings.EMBEDDING_MODEL_SIZE)
    yield
    app.mongo_conn.close()


app = FastAPI(lifespan=lifespan )


app.include_router(base.base_router)
app.include_router (data.data_router)


#uvicorn main:app --reload  --host 0.0.0.0 --port 5000
# run fastapi from main.py decoder app with reload (refresh directly)
#  any one can access run on port 5000

    


