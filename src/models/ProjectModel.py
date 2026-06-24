from .BaseDataModel import BaseDataModel
from .db_schemes import Project
from .enums.DataBaseEnum import DataBaseEnum
class ProjectModel(BaseDataModel):
    def __init__(self,db_client:object):
        super().__init__(db_client=db_client)
        self.collection=self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]
    
    @classmethod
    async def create_instance(cls,db_client:object):
        """
        Create an instance of ProjectModel and initialize the collection.
        because init_collection is an async function, we need to use await to wait for it to complete before returning the instance.
        but we cannot use await in the constructor, so we create a class method to create an instance of the class and initialize the collection.
        the index
        """
        instance = cls(db_client=db_client)
        await instance.init_collection()
        return instance
    
    
    async def init_collection(self):
        """
        Initialize the Project collection by creating indexes.
        """
        all_collections=await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_PROJECT_NAME.value not in all_collections:
            self.collection= self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]
            indexes=Project.get_indexes()
            for index in indexes:
                await self.collection.create_index(index["key"],name=index["name"],unique=index["unique"])
    #create a project if it does not exist
    async def create_project(self,project:Project):
    # ayncb because we are using motor client for mongodb which is asynchronous
        result = await self.collection.insert_one(project.dict(by_alias=True,exclude_unset=True))
        # await is used to wait for the result of the insert_one operation before proceeding to the next line of code. 
        # This is necessary because insert_one is an asynchronous operation that interacts with the database
        project.id=result.inserted_id
        return project
    
    async def get_project_or_create_one(self,project_id:str):
        # find_one is used to find a single document in the collection that matches the specified query.
        record = await self.collection.find_one({"project_id":project_id})
        if record is None:
            project =Project(project_id=project_id)
            project =await self.create_project(project)
            # if the project does not exist, create a new project and return it. If the project already exists,
            # return the existing project.
            
            return project
        # ** used to unpack the record dictionary and pass its key-value pairs as arguments to the Project constructor.
        return Project(**record)
    async def get_all_projects(self,page:int=1, page_size:int=10):
        #count the total number of documents in the collection
        total_documents=await self.collection.count_documents({})
        #count the total number of pages based on the page size
        total_pages=total_documents // page_size
        if total_documents % page_size > 0:
            total_pages += 1
            #we find the document we want by skipping the documents of the previous pages
            #and limit it to the page size
        cursor=self.collection.find().skip((page-1)*page_size).limit(page_size)
        projects=[]
        #the function find() returns a cursor, so we iterate on it and convert each document to a project object
        async for doc in cursor:
            projects.append(Project(**doc))
        return projects,total_pages