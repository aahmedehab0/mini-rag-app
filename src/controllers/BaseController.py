from helpers.confog import Settings , get_sttings


class BaseController:
    def __init__ (self):
        self.app_Settings = get_sttings()