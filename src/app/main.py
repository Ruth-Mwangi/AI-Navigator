from fastapi import FastAPI, Form, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import os
import spacy
import tensorflow as tf
import numpy as np
import pickle
from typing import List, Tuple
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, '../../')
sys.path.append(src_path)

from app.services.classify_service import classify_data_request
from app.services.data_retrieval_service import GenerateScatterPlot
from models.sentence import Sentence
from models.classification_response import ClassificationResponse
from models.token import Token
from models.user_in_db import UserInDB
from services.authentication import fake_hash_password



# Initialize FastAPI app
app = FastAPI()

intent_function_mapping = {
    # "GenerateBarChart": GenerateBarChart,
    # "GenerateLineChart": GenerateLineChart,
    # "GeneratePieChart": GeneratePieChart,
    "GenerateScatterPlot": GenerateScatterPlot,
    # "GenerateHeatmap": GenerateHeatmap,
    # "GenerateHistogram": GenerateHistogram
}
fake_users_db = {
    "user": {
        "username": "user",
        "full_name": "John Doe",
        "email": "user@example.com",
        "hashed_password": "fakehashedpassword",
        "disabled": False,
    }
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# @app.post("/get_response", response_class=JSONResponse)
# async def get_response(message: str = Form(...)):
#     # Here, you would process the user's message and generate a response
#     # For now, let's just echo the message back
#     response_message = f"You said: {message}"
#     return {"response": response_message}
# from fastapi.responses import JSONResponse
# from app.models.classification_response import ClassificationResponse

@app.post("/get_response", response_model=ClassificationResponse)
async def get_response(sentence_request: Sentence, token: str = Depends(oauth2_scheme)):
    sentence = sentence_request.text
    classification_response = classify_data_request(sentence)
    intent = classification_response.intent
    buf = None
    if intent in intent_function_mapping:
        buf = intent_function_mapping[intent](classification_response)
    else:
        print(f"No function mapped for intent: {intent}")

    if buf:
        return StreamingResponse(buf, media_type="image/png")
    else:
        return classification_response

@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = "fakejwttoken"  # Simplified token generation for demo
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/classify", response_model=ClassificationResponse)
async def classify(sentence_request: Sentence, token: str = Depends(oauth2_scheme)):
    sentence = sentence_request.text
    classification_response = classify_data_request(sentence)
    intent = classification_response.intent
    buf = None
    if intent in intent_function_mapping:
        buf = intent_function_mapping[intent](classification_response)
    else:
        print(f"No function mapped for intent: {intent}")

    if buf:
        return StreamingResponse(buf, media_type="image/png")
    else:
        return classification_response
    # return classification_response

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)