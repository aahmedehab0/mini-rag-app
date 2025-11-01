from helpers import get_setings , Settings

class BaseDataModel :
    def __init__(self , db_client:object):
        self.db_client = db_client
        self.get_setings = get_setings()
