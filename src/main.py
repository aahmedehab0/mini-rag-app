from fastapi import FastAPI 
from routes import base , data ,nlp
from motor.motor_asyncio import AsyncIOMotorClient
from helpers import get_setings
from contextlib import asynccontextmanager
from stores.llm import LLMProviderFactory
from stores.vectordb import VectorDBProviderFactory
from stores.llm.templates import TemplateParser


@asynccontextmanager
async def lifespan(app: FastAPI):
    #define copy of .env variables
    settings = get_setings()

    #define mongo connection
    app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)  
    #define mongo database
    app.db_client = app.mongo_conn [settings.MONGODB_DATABASE]  

    #get configs settings for llm provider
    llm_provider_factory = LLMProviderFactory(settings)        
    vectordb_provide_factory = VectorDBProviderFactory(settings)

    # generation client
    app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id = settings.GENERATION_MODEL_ID)

    # embedding client
    app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID,
                                             embedding_size=settings.EMBEDDING_MODEL_SIZE)
    # vectordb client
    app.vectordb_client = vectordb_provide_factory.create(
        provider=settings.VECTOR_DB_BACKEND
        )
    app.vectordb_client.connect()

    app.template_parser = TemplateParser(
        language=settings.PRIMARY_LANG,
        default_language=settings.DEFAULT_LANG,
    )

    #span stop
    yield
    app.mongo_conn.close()
    app.vectordb_client.disconnect()

app = FastAPI(lifespan=lifespan )


app.include_router(base.base_router)
app.include_router (data.data_router)
app.include_router(nlp.nlp_router)


#uvicorn main:app --reload  --host 0.0.0.0 --port 5000
# run fastapi from main.py decoder app with reload (refresh directly)
#  any one can access run on port 5000

    


