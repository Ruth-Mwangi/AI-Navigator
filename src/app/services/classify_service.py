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

# Define file paths
ner_model_path = os.path.join(current_dir, "../../data/ner_model/model-best")
intent_model_path = os.path.join(current_dir, "../../data/intent_model")
label_pickle_path = os.path.join(current_dir, "../../data/intent_model/label_binarizer.pkl")

# Load the entire intent classifier model
def load_intent_classifier():
    return tf.keras.models.load_model(intent_model_path)

# Load the trained NER model
def load_ner_model():
    return spacy.load(ner_model_path)

# Load the saved LabelBinarizer
def load_label_binarizer():
    with open(label_pickle_path, 'rb') as file:
        return pickle.load(file)

# Combine intent classification and NER
def classify_data_request(sentence)->ClassificationResponse:
    
    intent_classifier = load_intent_classifier()
    ner_model = load_ner_model()
    binarizer = load_label_binarizer()  
    

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
    # classification_response = ClassificationResponse.parse_obj(response)
   
    
    return classification_response


