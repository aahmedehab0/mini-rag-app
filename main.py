from fastapi import FastAPI
app = FastAPI()

@app.get("/welcome")
def welcome():
    return {
        "message" : "Hello From Fast Api"
    }

#uvicorn main:app --reload  --host 0.0.0.0 --port 5000
# run fastapi from main.py decoder app with reload (refresh directly)
#  any one can access run on port 5000
