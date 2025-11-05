from .. import LLMInterface                                         #class have the construct of any provider
from .. import CoHereEnums , DocumentTypeEnum                       # some fixed texts
import cohere
import logging

class CoHereProvider(LLMInterface):               

    def __init__(self, api_key: str,
                       default_input_max_characters: int=1000,
                       default_generation_max_output_tokens: int=1000,
                       default_generation_temperature: float=0.1):
        
        #api key to work on api
        self.api_key = api_key

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

        #client for cohere (object who can connect to API)
        self.client = cohere.Client(api_key=self.api_key)

        #logger in logs with this class name
        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model_id: str):
        """id for generation model (we can change it after object initilzation)"""
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: int):
        """id for embeding model (we can change it after object initilzation , 
        if we change model we must change vector size) """
        
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    def process_text(self, text: str):
        """process input text to remove spaces at start and end and take only max input size """
        return text[:self.default_input_max_characters].strip()

    def generate_text(self, prompt: str, chat_history: list=[], max_output_tokens: int=None,
                            temperature: float = None):
        """process to validate output and return it"""

        # validate if client not efined
        if not self.client:
            self.logger.error("CoHere client was not set")
            return None
        
        #validate if generation model was not set
        if not self.generation_model_id:
            self.logger.error("Generation model for CoHere was not set")
            return None
        
        # if max output token passed into function take it else take default in init class
        max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens
        # if tempreature passed into function take it else take default in init class
        temperature = temperature if temperature else self.default_generation_temperature

        # response of output text
        response = self.client.chat(
            model = self.generation_model_id,
            chat_history = chat_history,
            message = self.process_text(prompt),
            temperature = temperature,
            max_tokens = max_output_tokens
        )

        #validate response output
        if not response or not response.text:
            self.logger.error("Error while generating text with CoHere")
            return None
        
        # return output text 
        return response.text
    
    def embed_text(self, text: str, document_type: str = None):
        """
        Generate embeddings for a given text using the current embedding model.
        
        Args:
            text (str): Input text to embed.
            document_type (str, optional): Whether it's a document or a query.
        
        Returns:
            list[float]: The vector representation of the text.
        """
        if not self.client:
            self.logger.error("CoHere client was not set")
            return None
        
        # validate if embeding model was not set
        if not self.embedding_model_id:
            self.logger.error("Embedding model for CoHere was not set")
            return None
        
        #input type:  document or query (question from user)
        input_type = CoHereEnums.DOCUMENT
        if document_type == DocumentTypeEnum.QUERY:
            input_type = CoHereEnums.QUERY

        # embeding response
        response = self.client.embed(
            model = self.embedding_model_id,
            texts = [self.process_text(text)],
            input_type = input_type,
            embedding_types=['float'],
        )
        #validate embeding out if empty or have any missing
        if not response or not response.embeddings or not response.embeddings.float:
            self.logger.error("Error while embedding text with CoHere")
            return None
        
        # return embeding output
        return response.embeddings.float[0]
    
     # convert promt into dict (promt must be dict)
    def construct_prompt(self, prompt: str, role: str):
        
        return {
            "role": role,
            "text": self.process_text(prompt)
        }