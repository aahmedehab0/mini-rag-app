import os
#chose template of arabic or english
class TemplateParser:

    def __init__(self, language: str=None, default_language='en'):
        # get current directory
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        # set default language
        self.default_language = default_language
        #language user will type with
        self.language = None
        # set the language user will type with
        self.set_language(language)

    
    def set_language(self, language: str):
        # validate language
        if not language:
            self.language = self.default_language

        # if language which user choose is exist in locels set it else set default language 
        language_path = os.path.join(self.current_path, "locales", language)
        if os.path.exists(language_path):
            self.language = language
        else:
            self.language = self.default_language


    def get(self, group: str, key: str, vars: dict={}):

        #validate group and key
        if not group or not key:
            return None
        
        group_path = os.path.join(self.current_path, "locales", self.language, f"{group}.py" )
        targeted_language = self.language

        # validate file in language folder if not exist select default language
        if not os.path.exists(group_path):
            group_path = os.path.join(self.current_path, "locales", self.default_language, f"{group}.py" )
            targeted_language = self.default_language

        if not os.path.exists(group_path):
            return None
        
        # import group module (imoprt rag.py in language file)
        module = __import__(f"stores.llm.templates.locales.{targeted_language}.{group}", fromlist=[group])

        #validate module
        if not module:
            return None
        #get function key from rag.py
        key_attribute = getattr(module, key)
        #replace inputs with vars
        return key_attribute.substitute(vars)