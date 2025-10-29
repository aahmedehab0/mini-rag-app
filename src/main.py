from fastapi import FastAPI
from dotenv import load_dotenv
load_dotenv('.env')

from routes import base



app = FastAPI()
app.include_router(base.base_router)



#
# run fastapi from main.py decoder app with reload (refresh directly)
#  any one can access run on port 5000