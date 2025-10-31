from .BaseDataModel import BaseDataModel
from enums.DataBaseEnums import DataBaseEnum
from db_schemes import Project

class ProjectDataModel (BaseDataModel):
    def __init__(self, db_client : object):
        super().__init__(db_client = db_client)
        self.collection = self.db_client [DataBaseEnum.COLLECTION_PROJECT_NAME.value]

    async def crate_projrct (self , Project : Project):
        result = await self.collection.insert_one (Project.dict())