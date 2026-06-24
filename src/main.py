from fastapi import FastAPI
from routes import base,data
#for connection to the database we will use the motor library which is an asynchronous driver for MongoDB
# it allows us to perform database operations without blocking the main thread
# which is essential for maintaining the responsiveness of our FastAPI application
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings

app=FastAPI()
# we will use the startup event to initialize the database connection when the application starts
# and the shutdown event to close the database connection when the application shuts down
# this ensures that we have a persistent connection to the database throughout the lifecycle of the application 
# that we properly clean up resources when they are no longer needed.
@app.on_event("startup")
async def startup_db_client():
    settings=get_settings()
    app.mongo_conn=AsyncIOMotorClient(settings.MONGODB_URI)
    app.db_client=app.mongo_conn[settings.MONGODB_DB_NAME]
    
@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongo_conn.close()
    
app.include_router(base.base_router)
app.include_router(data.data_router)


