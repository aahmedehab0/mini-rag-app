from fastapi import FastAPI 
from routes import base , data




app = FastAPI()
app.include_router(base.base_router)
app.include_router (data.data_router)


#uvicorn main:app --reload  --host 0.0.0.0 --port 5000
# run fastapi from main.py decoder app with reload (refresh directly)
#  any one can access run on port 5000