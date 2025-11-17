from .. import  LLMInterface                       #class have the construct of any provider
from .. import  OpenAIEnums                        # some fixed texts
from openai import OpenAI                          #open ai library

import logging

class OpenAIProvider (LLMInterface):
    def __init__(self, api_key: str, api_url: str=None,
                       default_input_max_characters: int=1000,
                       default_generation_max_output_tokens: int=1000,
                       default_generation_temperature: float=0.1):
        
        #api key to work on api
        self.api_key = api_key 
        #api url 
        self.api_url = api_url                                                     
        #max input and max output 
        self.default_input_max_characters = default_input_max_characters           
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        #temperature is avalue between 0 and 2 for ceritavity 
        #0-> Very logical  , 0.3->Slight balance  , 0.7-> More creative , 1.0->High randomness , >1.3Very random (can be inlogocal)
        self.default_generation_temperature = default_generation_temperature
        #model id which generate text like :gpt ,....
        self.generation_model_id = None
        #embeding model
        self.embedding_model_id = None
        #embeding size (dimensions of vector it fixed for model but should be passed)
        self.embedding_size = None


        #client for open ai (object who can connect to API)
        self.client = OpenAI(
            api_key = self.api_key,
            base_url =  self.api_url if self.api_url and len(self.api_url) else None
        )

        self.enums = OpenAIEnums

        #logger in logs with this class name
        self.logger = logging.getLogger(__name__)

    #id for generation model (we can change it after object initilzation)
    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id

   #id for embeding model (we can change it after object initilzation , if we change model we must change vector size) 
    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    # process input text to remove spaces at start and end and take only max input size
    def process_text(self, text: str):
        return text[:self.default_input_max_characters].strip()
    
    # process to validate dict output and return it
    def generate_text(self, prompt: str, chat_history: list=[], max_output_tokens: int=None,
                            temperature: float = None):
        
        if not self.client:                                # validate if client not efined
            self.logger.error("OpenAI client was not set")
            return None

        if not self.generation_model_id:                  #validate if generation model was not set
            self.logger.error("Generation model for OpenAI was not set")
            return None
        
        # if max output token passed into function take it else take default in init class
        max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens
        # if tempreature passed into function take it else take default in init class
        temperature = temperature if temperature else self.default_generation_temperature
        #add promt input user to list of chat history
        chat_history.append(
            self.construct_prompt(prompt=prompt, role=OpenAIEnums.USER.value)
        )
        # response of output text
        response = self.client.chat.completions.create(
            model = self.generation_model_id,
            messages = chat_history,
            max_tokens = max_output_tokens,
            temperature = temperature
        )
        #validate response output
        if not response or not response.choices or len(response.choices) == 0 or not response.choices[0].message:
            self.logger.error("Error while generating text with OpenAI")
            return None
        # return output text 
        return response.choices[0].message.content

    #embeding input user
    def embed_text(self, text: str, document_type: str = None):
        
        if not self.client:                                          # validate if client not defined
            self.logger.error("OpenAI client was not set")
            return None

        if not self.embedding_model_id:                             # validate if embeding model was not set
            self.logger.error("Embedding model for OpenAI was not set")
            return None
        
        # embeding response
        response = self.client.embeddings.create(                   
            model = self.embedding_model_id,
            input = text,
        )
        #validate embeding out if empty or have any missing 
        if not response or not response.data or len(response.data) == 0 or not response.data[0].embedding:
            self.logger.error("Error while embedding text with OpenAI")
            return None

        return response.data[0].embedding
    # convert promt into dict (promt must be dict)
    def construct_prompt(self, prompt: str, role: str):
        return {
            "role": role,
            "content": prompt
        }
    
