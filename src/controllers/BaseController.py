from helpers.confog import Settings , get_sttings
import os

class BaseController:
    def __init__ (self):
        self.app_Settings = get_sttings()
        self.base_dir = os.path.dirname(os.path.dirname(__file__))
        self.file_dir = os.path.join(self.base_dir,
                                     "/asset/files"
        )
        
        print(self.base_dir )