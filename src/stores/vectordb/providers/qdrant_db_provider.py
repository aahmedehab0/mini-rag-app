from qdrant_client import models, QdrantClient #qdrant library which is vector for database
from .. import VectorDBInterface               #interface for any vector database
from .. import DistanceMethodEnums             #some fixed texts related to search database
import logging                                 
from typing import List                        #list type

class QdrantDBProvider(VectorDBInterface):

    def __init__(self, db_path: str, distance_method: str):

        #client in database will defined in method
        self.client = None   
        #path of vectors where it stored          
        self.db_path = db_path
        #distane typr for search
        self.distance_method = None

        #switch between cosine or dot product
        if distance_method == DistanceMethodEnums.COSINE.value:
            self.distance_method = models.Distance.COSINE
        elif distance_method == DistanceMethodEnums.DOT.value:
            self.distance_method = models.Distance.DOT
            
        #logger in logs with this class name
        self.logger = logging.getLogger(__name__)


    def connect(self):
        # Initialize a Qdrant client that connects to the local database stored at the given file path.
        # The 'path' parameter tells Qdrant to use a local (on-disk) instance instead of a remote server.
        self.client = QdrantClient(path=self.db_path)

    def disconnect(self):
        #remove client to stop Qdrant
        self.client = None

    def is_collection_existed(self, collection_name: str) -> bool:
        # Check if a collection with the given name already exists in the Qdrant database.
        # Returns True if the collection exists, otherwise False.
        return self.client.collection_exists(collection_name=collection_name)
    
    def list_all_collections(self) -> List:
        # Retrieve and return a list of all collections stored in the Qdrant database.
        # Each collection represents a separate group of vectors and metadata.
        return self.client.get_collections()
    
    def get_collection_info(self, collection_name: str) -> dict:
        # Get detailed information about a specific collection in the Qdrant database.
        # This includes metadata such as vector size, distance metric, and configuration details.
        return self.client.get_collection(collection_name=collection_name)

    
    def delete_collection(self, collection_name: str):
        #delete collection from Qdrant database.
        #check first if collection exist or not
        if self.is_collection_existed(collection_name):
            return self.client.delete_collection(collection_name=collection_name)
        
    def create_collection(self, collection_name: str, 
                                embedding_size: int,
                                do_reset: bool = False):
        """
        create new collection and reset .
        
        Args:
            collection_name (str): Input collection name for function.
            embedding_size (int): size of vectors in collection.
            do_reset ( bool , optional ):if collection exist delete all vectors
        Returns:
            boolean: True if collection created else : False
        """
        # if reset true  delete all vectors if collection is exist
        if do_reset:
            _ = self.delete_collection(collection_name=collection_name)
        
        # if collection not exist
        if not self.is_collection_existed(collection_name):
            _ = self.client.create_collection(        
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=embedding_size,
                    distance=self.distance_method
                )
            )

            return True
        
        return False
    
    def insert_one(self, collection_name: str, text: str, vector: list,
                         metadata: dict = None, 
                         record_id: str = None):
        """
        insert only one record in collection.
        
        Args:
            collection_name (str): Input collection name for function.
            text (str): input texts data of collection which will stored in Qdrant database.
            vector ( list ): input vectors data of collection which will stored in Qdrant database.
            metadata (dict , optional): metadata of texts if not exist will be None
            record_id (str , optional): unique id for collection if not exist will be None
        Returns:
            boolean: True if collection inserted else : False
        """
        
        if not self.is_collection_existed(collection_name):
            self.logger.error(f"Can not insert new record to non-existed collection: {collection_name}")
            return False
        
        try:
            _ = self.client.upload_records(
                collection_name=collection_name,
                records=[
                    models.Record(
                        vector=vector,
                        id = record_id,
                        payload={
                            "text": text, "metadata": metadata
                        }
                    )
                ]
            )
        except Exception as e:
            self.logger.error(f"Error while inserting batch: {e}")
            return False

        return True
    
    def insert_many(self, collection_name: str, texts: list, 
                          vectors: list, metadata: list = None, 
                          record_ids: list = None, batch_size: int = 50):
        """
        insert many records in collection in Qdrant database.
        
        Args:
            collection_name (str): Input collection name for function.
            text (str): input texts data of collection which will stored in Qdrant database.
            vectors ( list ): input vectors data of collection which will stored in Qdrant database.
            metadata (dict , optional): metadata of texts if not exist will be None
            record_ids (str , optional): unique id for collection if not exist will be None
            batch_size (int , optional) : divide records to batches
        Returns:
            boolean: True if collection inserted else : False
        """
        if metadata is None:
            metadata = [None] * len(texts)

        if record_ids is None:
            record_ids = [None] * len(texts)

        for i in range(0, len(texts), batch_size):
            batch_end = i + batch_size
            #divide texts and vectors and metadata into batches
            batch_texts = texts[i:batch_end]
            batch_vectors = vectors[i:batch_end]
            batch_metadata = metadata[i:batch_end]

            # convert data int records
            batch_records = [
                models.Record(
                    vector=batch_vectors[x],
                    id = record_ids[x],
                    payload={
                        "text": batch_texts[x], "metadata": batch_metadata[x]
                    }
                )

                for x in range(len(batch_texts))       
            ]

            try:
                _ = self.client.upload_records(
                    collection_name=collection_name,
                    records=batch_records,
                )
            except Exception as e:
                self.logger.error(f"Error while inserting batch: {e}")
                return False

        return True
        
    def search_by_vector(self, collection_name: str, vector: list, limit: int = 5):
        """
        search for vector and similarity vector collection and return (limit) vectors .
        
        Args:
            collection_name (str):  collection name will search.
            vector ( list ): vector will search in collection.
            limit (int , optional) : ;n. of collections will return.
        Returns:
            list (collections): vectors have most similarity for input vector
        """    

        return self.client.search(
            collection_name=collection_name,
            query_vector=vector,
            limit=limit
        )