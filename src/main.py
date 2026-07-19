from fastapi import FastAPI
from routes import base,data, nlp
#for connection to the database we will use the motor library which is an asynchronous driver for MongoDB
# it allows us to perform database operations without blocking the main thread
# which is essential for maintaining the responsiveness of our FastAPI application
#from motor.motor_asyncio import AsyncIOMotorClient mongodb related
from helpers.config import get_settings
from stores.llm.LLMProviderFactory import LLMProviderFactory,LLMEnums
from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory
from stores.llm.templates.template_parser import TemplateParser
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

app=FastAPI()
# we will use the startup event to initialize the database connection when the application starts
# and the shutdown event to close the database connection when the application shuts down
# this ensures that we have a persistent connection to the database throughout the lifecycle of the application 
# that we properly clean up resources when they are no longer needed.
@app.on_event("startup")
async def startup_span():
    settings=get_settings()
    #we changed the database into postgres
    #app.mongo_conn=AsyncIOMotorClient(settings.MONGODB_URI)
    #app.db_client=app.mongo_conn[settings.MONGODB_DB_NAME]
    
    postgres_conn = f"postgresql+asyncpg://{settings.POSTGRES_USERNAME}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_MAIN_DATABASE}"

    app.db_engine = create_async_engine(postgres_conn)
    app.db_client = sessionmaker(
        app.db_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    
    llm_provider_factory=LLMProviderFactory(settings)
    vectordb_provider_factory=VectorDBProviderFactory(config=settings,db_client=app.db_client)
    
    
    app.generation_client=llm_provider_factory.create(settings.GENERATION_BACKEND)
    
    app.generation_client.set_generative_model(settings.GENERATION_MODEL_ID)
    
    
    app.embedding_client=llm_provider_factory.create(settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(settings.EMBEDDING_MODEL_ID,settings.EMBEDDING_MODEL_SIZE)
    
    
    app.vectordb_client=vectordb_provider_factory.create(provider=settings.VECTOR_DB_BACKEND)
    await app.vectordb_client.connect()
    
    app.template_parser=TemplateParser(language=settings.PRIMARY_LANG,default_language=settings.DEFAULT_LANG)    

@app.on_event("shutdown")
async def shutdown_span():
    #app.mongo_conn.close()
    await app.db_engine.dispose()
    await app.vectordb_client.disconnect()
#app.router.lifespan.on_startup.append(startup_span)
#app.router.lifespan.on_shutdown.append(shutdown_span)

app.on_event("startup")(startup_span)
app.on_event("shutdown")(shutdown_span)

app.include_router(base.base_router)
app.include_router(nlp.nlp_router)  
app.include_router(data.data_router)


