from fastapi import FastAPI
from routes import base,data, nlp
#for connection to the database we will use the motor library which is an asynchronous driver for MongoDB
# it allows us to perform database operations without blocking the main thread
# which is essential for maintaining the responsiveness of our FastAPI application
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings
from stores.llm.LLMProviderFactory import LLMProviderFactory,LLMEnums
from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory


app=FastAPI()
# we will use the startup event to initialize the database connection when the application starts
# and the shutdown event to close the database connection when the application shuts down
# this ensures that we have a persistent connection to the database throughout the lifecycle of the application 
# that we properly clean up resources when they are no longer needed.
@app.on_event("startup")
async def startup_span():
    settings=get_settings()
    app.mongo_conn=AsyncIOMotorClient(settings.MONGODB_URI)
    app.db_client=app.mongo_conn[settings.MONGODB_DB_NAME]
    
    llm_provider_factory=LLMProviderFactory(settings)
    vectordb_provider_factory=VectorDBProviderFactory(settings)
    
    
    app.generation_client=llm_provider_factory.create(settings.GENERATION_BACKEND)
    
    app.generation_client.set_generative_model(settings.GENERATION_MODEL_ID)
    
    
    app.embedding_client=llm_provider_factory.create(settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(settings.EMBEDDING_MODEL_ID,settings.EMBEDDING_MODEL_SIZE)
    
    
    app.vectordb_client=vectordb_provider_factory.create(provider=settings.VECTOR_DB_BACKEND)
    app.vectordb_client.connect()
          
@app.on_event("shutdown")
async def shutdown_span():
    app.mongo_conn.close()
    app.vectordb_client.disconnect()
#app.router.lifespan.on_startup.append(startup_span)
#app.router.lifespan.on_shutdown.append(shutdown_span)

app.on_event("startup")(startup_span)
app.on_event("shutdown")(shutdown_span)

app.include_router(base.base_router)
app.include_router(nlp.nlp_router)  
app.include_router(data.data_router)


