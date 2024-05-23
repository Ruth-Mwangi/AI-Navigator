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
static_path = os.path.join(current_dir,'static')
templates_path = os.path.join(current_dir,'templates')

from services.classify_service import classify_data_request
from services.data_retrieval_service import GenerateBarChart, GeneratePieChart, GenerateScatterPlot
from models.sentence import Sentence
from models.classification_response import ClassificationResponse
from models.token import Token
from models.user_in_db import UserInDB
from services.authentication import authenticate_user, create_access_token, verify_token



# Initialize FastAPI app
app = FastAPI()

intent_function_mapping = {
    "GenerateBarChart": GenerateBarChart,
    # "GenerateLineChart": GenerateLineChart,
    "GeneratePieChart": GeneratePieChart,
    "GenerateScatterPlot": GenerateScatterPlot,
    # "GenerateHeatmap": GenerateHeatmap,
    # "GenerateHistogram": GenerateHistogram
}


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
app.mount("/static", StaticFiles(directory=static_path), name="static")
templates = Jinja2Templates(directory=templates_path)

@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})



@app.post("/data_request", response_model=ClassificationResponse)
async def get_response(sentence_request: Sentence, token: str = Depends(oauth2_scheme)):
    username = verify_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")

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
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token = create_access_token(user.username)
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/classify", response_model=ClassificationResponse)
async def classify(sentence_request: Sentence, token: str = Depends(oauth2_scheme)):
    username = verify_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")

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