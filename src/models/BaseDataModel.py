from helpers import get_setings , Settings
from db_schemes import data_chunk
from enums.DataBaseEnums import DataBaseEnum

class BaseDataModel :
    def __init__(self , db_client:object):
        self.db_client = db_client
        self.get_setings = get_setings()
