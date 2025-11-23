APP_NAME = "mini-rag"
APP_VERSION = "0.1"
# ========================= backend Config =========================
FILE_ALLOWED_TYPES = ["text/plain" , "application/pdf"]
FILE_MAX_SIZE = 5
FILE_DEFAULT_CHUNK_SIZE = 512000

POSTGRES_USERNAME="postgres"
POSTGRES_PASSWORD="PASSWORD"
POSTGRES_HOST="pgvector"
POSTGRES_PORT=5432
POSTGRES_MAIN_DATABASE="minirag"
# ========================= LLM Config =========================
GENERATION_BACKEND = "OPENAI"
EMBEDDING_BACKEND = "COHERE"
# ========================= open ai Config =========================
OPENAI_API_KEY=""
OPENAI_API_URL=
COHERE_API_KEY=""
# ========================= model Config =========================
GENERATION_MODEL_ID="gpt-3.5-turbo-0125"
EMBEDDING_MODEL_ID="embed-multilingual-light-v3.0"
EMBEDDING_MODEL_SIZE=384
# ========================= input promt Config =========================
INPUT_DAFAULT_MAX_CHARACTERS=1024
GENERATION_DAFAULT_MAX_TOKENS=200
GENERATION_DAFAULT_TEMPERATURE=0.1
# ========================= Vector DB Config =========================
VECTOR_DB_BACKEND_LITERAL = ["QDRANT", "PGVECTOR"]
VECTOR_DB_BACKEND="QDRANT"
VECTOR_DB_PATH="qdrant_db"
VECTOR_DB_DISTANCE_METHOD="cosine"
VECTOR_DB_PGVEC_INDEX_THRESHOLD = 100 
# ========================= Template Configs =========================
PRIMARY_LANG = "en"
DEFAULT_LANG = "en"
CELERY_BROKER_URL="amqp://minirag_user:minirag_pass@localhost:port/vhost" #store tasks which not excuted 
CELERY_RESULT_BACKEND="redis://:pass@localhost:port/0" # store result of tasks , task situation , error , excute time..
CELERY_TASK_SERIALIZER="json"    
CELERY_TASK_TIME_LIMIT=600           #600sec : Time limit for task
CELERY_TASK_ACKS_LATE=false           # acknowlegment when finshed , if True acknowlegment qhen recived
CELERY_WORKER_CONCURRENCY=2            # worker do 2 tasks
CELERY_FLOWER_PASSWD= ""