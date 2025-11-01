from .BaseDataModel import BaseDataModel
from .enums import DataBaseEnum
from .db_schemes import Project


class ProjectModel (BaseDataModel):
    def __init__(self, db_client : object):
        super().__init__(db_client = db_client)
        self.collection = self.db_client [DataBaseEnum.COLLECTION_PROJECT_NAME.value]

    async def crate_projrct (self , project : Project):
        result = await self.collection.insert_one (project.model_dump(by_alias= True ,exclude_unset=True))
        project._id = result.inserted_id
        return project
    
    async def get_project_or_create_one (self ,project_id : str):
        record = await self.collection.find_one ({
        "project_id" : project_id
        })

        if record is None:
            project = Project (project_id = project_id )
            project = await self.crate_projrct(project = project)
            return project
        
        return Project(**record)
        
    
    async def get_all_pages(self , page :int = 1 , page_szie :int = 10):

        total_documents = self.collection.count_documensts ({})
        total_pages = total_documents //page_szie
        if total_documents % page_szie >0:
            total_pages +=1
        cursor = self.collection.find ().skip ((page-1) *10).limit (page_szie)
        projects = []
        async for document in cursor:
            projects.append(
                Project (**document)
                )
        return projects , total_pages

    