import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, '../../')
sys.path.append(src_path)
import json

import pickle

import numpy as np
import spacy
import tensorflow as tf
import tensorflow_text as text 
from spacy.tokens import DocBin
from tqdm import tqdm
from spacy.util import filter_spans


from app.models.classification_response import ClassificationResponse, Entity

# Get the directory of the current script (chatbot.py)
current_dir = os.path.dirname(os.path.abspath(__file__))



# Combine intent classification and NER
def classify_data_request(sentence,intent_classifier,ner_model,binarizer)->ClassificationResponse:
    
    # Intent classification
    intent_prediction = intent_classifier.predict([sentence])
    intent_index = np.argmax(intent_prediction)
    intent = binarizer.classes_[intent_index]

    

    # Named Entity Recognition
    doc = ner_model(sentence)
    entities = [{"text": ent.text, "start": ent.start_char, "end": ent.end_char, "label": ent.label_} for ent in doc.ents]
    
    # Construct the response JSON
    response = {
        "intent": intent,
        "entities": entities
    }
    
    # Create a ClassificationResponse object
    classification_response = ClassificationResponse(request=sentence,intent=intent, entities=[Entity(**entity) for entity in entities])
   
    
    return classification_response


