from .BaseDataModel import BaseDataModel
from .enums import DataBaseEnum
from .db_schemes import Asset

class ProjectModel (BaseDataModel):
    def __init__(self, db_client : object):
        super().__init__(db_client = db_client)
        self.collection = self.db_client [DataBaseEnum.COLLECTION_PROJECT_NAME.value]
    
    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collection()
        return instance
    
    async def init_collection (self):
        all_collections = await self.db_client.list_collection_names()
        if  DataBaseEnum.COLLECTION_PROJECT_NAME.value not in all_collections:
            indexes = Asset.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index["key"],
                    name = index["name"],
                    unique = index ["unique"]
                )
    async def crate_projrct (self , asset : Asset):
        result = await self.collection.insert_one (asset.model_dump(by_alias= True ,exclude_unset=True))
        asset._id = result.inserted_id
        return asset