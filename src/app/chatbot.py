import numpy as np
import spacy
from spacy.tokens import DocBin
from tqdm import tqdm
from spacy.util import filter_spans
import pickle
import tensorflow as tf
import tensorflow_text as text  # Import TensorFlow Text to register the ops
import json

import os
# Get the directory of the current script (chatbot.py)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the absolute path to the saved model file
ner_model_path = os.path.join(current_dir, "../data/ner_model/model-best")
intent_model_path = os.path.join(current_dir, "../data/intent_model")
label_pickle_path = os.path.join(current_dir, "../data/intent_model/label_binarizer.pkl")

# Intent Classifier Code
def load_intent_classifier():
    # Load the entire model using the constructed absolute path
    classifier_model = tf.keras.models.load_model(intent_model_path)
    return classifier_model

# Named Entity Recognition (NER) Model Code
def load_ner_model():
    # Load the trained NER model
    nlp_trained_model = spacy.load(ner_model_path)
    return nlp_trained_model

# Load the saved LabelBinarizer
def load_label_binarizer():
    with open(label_pickle_path, 'rb') as file:
        binarizer = pickle.load(file)
    return binarizer

# Define the function that combines both models
def combined_intent_and_ner(sentence, intent_classifier, ner_model, binarizer):
    # Intent classification
    intent_prediction = intent_classifier.predict([sentence])

    intent_prediction = np.array(intent_prediction)
    
    intent_index = np.argmax(intent_prediction)
    intent_confidence = tf.keras.activations.softmax(tf.convert_to_tensor(intent_prediction), axis=-1).numpy().max()
    intent = binarizer.classes_[intent_index]  # Assuming 'binarizer' is defined and has the class labels

    # Named Entity Recognition
    doc = ner_model(sentence)
    entities = [(ent.text, ent.start_char, ent.end_char, ent.label_) for ent in doc.ents]

    return intent, intent_confidence, entities

# Load both models
intent_classifier = load_intent_classifier()
ner_model = load_ner_model()
binarizer = load_label_binarizer()  # Load the LabelBinarizer

# Example sentence
sentence = "Please show me a scatter plot of country Kenya and product type Tshirt"

# Get intent and entities
intent, intent_confidence, entities = combined_intent_and_ner(sentence, intent_classifier, ner_model, binarizer)

print(f"Intent: {intent} (Confidence: {intent_confidence})")
print("Entities:")
print("Entities:")
entities_dict = {
    "entities": [
        {
            "text": entity[0],
            "start": entity[1],
            "end": entity[2],
            "label": entity[3]
        }
        for entity in entities
    ]
}

# Convert the dictionary to a JSON string
entities_json = json.dumps(entities_dict, indent=4)

# Print the JSON string
# print("Entities as JSON:")
print(entities_json)
output = {
    "visualization": None,
    "data_aggregation": None,
    "time_period": None,
    "variable": [],
    "date":[]
}

# Variables to keep track of the last VARIABLE type
current_variable = None
variable_values = []
current_date = None
date_values = []
# Iterate through the entities and populate the output dictionary
for entity in entities_dict['entities']:
    if entity["label"] == "VISUALIZATION":
        output["visualization"] = entity["text"]
    elif entity["label"] == "DATA_AGGREGATION":
        output["data_aggregation"] = entity["text"]
    elif entity["label"] == "TIME_PERIOD":
        output["time_period"] = entity["text"]
    elif entity["label"] == "VARIABLE":
        # If there was a previous variable and values, save it
        if current_variable:
            output["variable"].append({current_variable.lower(): variable_values})
        # Start tracking a new variable
        current_variable = entity["text"]
        variable_values = []
    elif entity["label"] == "DATE":
        # If there was a previous variable and values, save it
        if current_date:
            output["date"].append({current_date.lower(): date_values})
        # Start tracking a new variable
        current_date = entity["text"]
        date_values = []
    elif entity["label"] == "VALUE" and current_variable:
        # Add value to the current variable
        variable_values.append(entity["text"])
    elif entity["label"] == "VALUE" and current_date:
        # Add value to the current variable
        date_values.append(entity["text"])

# After the loop, save the last variable if any
if current_variable:
    output["variable"].append({current_variable: variable_values})
    # Add the variable with an empty array if no values were found
if current_date:
    output["date"].append({current_date.lower(): date_values})
    # Add the variable with an empty array if no values were found
    

# Convert to JSON and print the result
result_json = json.dumps(output, indent=4)
print(result_json)