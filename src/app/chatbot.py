import numpy as np
import pandas as pd
import spacy
from spacy.tokens import DocBin
from tqdm import tqdm
from spacy.util import filter_spans
import pickle
import tensorflow as tf
import tensorflow_text as text  # Import TensorFlow Text to register the ops
import json

import os
import pandas as pd
import matplotlib.pyplot as plt
# # Get the directory of the current script (chatbot.py)
# current_dir = os.path.dirname(os.path.abspath(__file__))

# # Construct the absolute path to the saved model file
# ner_model_path = os.path.join(current_dir, "../data/ner_model/model-best")
# intent_model_path = os.path.join(current_dir, "../data/intent_model")
# label_pickle_path = os.path.join(current_dir, "../data/intent_model/label_binarizer.pkl")

# # Intent Classifier Code
# def load_intent_classifier():
#     # Load the entire model using the constructed absolute path
#     classifier_model = tf.keras.models.load_model(intent_model_path)
#     return classifier_model

# # Named Entity Recognition (NER) Model Code
# def load_ner_model():
#     # Load the trained NER model
#     nlp_trained_model = spacy.load(ner_model_path)
#     return nlp_trained_model

# # Load the saved LabelBinarizer
# def load_label_binarizer():
#     with open(label_pickle_path, 'rb') as file:
#         binarizer = pickle.load(file)
#     return binarizer

# # Define the function that combines both models
# def combined_intent_and_ner(sentence, intent_classifier, ner_model, binarizer):
#     # Intent classification
#     intent_prediction = intent_classifier.predict([sentence])

#     intent_prediction = np.array(intent_prediction)
    
#     intent_index = np.argmax(intent_prediction)
#     intent_confidence = tf.keras.activations.softmax(tf.convert_to_tensor(intent_prediction), axis=-1).numpy().max()
#     intent = binarizer.classes_[intent_index]  # Assuming 'binarizer' is defined and has the class labels

#     # Named Entity Recognition
#     doc = ner_model(sentence)
#     entities = [(ent.text, ent.start_char, ent.end_char, ent.label_) for ent in doc.ents]

#     return intent, intent_confidence, entities

# # Load both models
# intent_classifier = load_intent_classifier()
# ner_model = load_ner_model()
# binarizer = load_label_binarizer()  # Load the LabelBinarizer

# # Example sentence
# sentence = "Show me a scatter plot of country Kenya and product type Tshirt"

# # Get intent and entities
# intent, intent_confidence, entities = combined_intent_and_ner(sentence, intent_classifier, ner_model, binarizer)

# print(f"Intent: {intent} (Confidence: {intent_confidence})")

# entities_dict = {
#     "intent": intent,
#     "entities": [
#         {
#             "text": entity[0],
#             "start": entity[1],
#             "end": entity[2],
#             "label": entity[3]
#         }
#         for entity in entities
#     ]
# }

# # Convert the dictionary to a JSON string
# entities_json = json.dumps(entities_dict, indent=4)




# Sample data
data = {
    "Country": ["Kenya", "Kenya", "USA", "USA", "Germany", "Germany", "India", "India"],
    "Product": ["Tshirt", "Shoes", "Tshirt", "Shoes", "Tshirt", "Shoes", "Tshirt", "Shoes"],
    "Sales": [150, 200, 300, 250, 180, 220, 260, 210],
    "Quantity": [500, 700, 1200, 950, 600, 750, 1100, 800]
}

# Create DataFrame
df = pd.DataFrame(data)
print(df)

# Create a scatter plot
plt.figure(figsize=(12, 8))

# Iterate through unique product types to plot each separately
for product in df['Product'].unique():
    subset = df[df['Product'] == product]
    plt.scatter(subset['Sales'], subset['Quantity'], label=product)

# Adding titles and labels
plt.title('Sales vs. Quantity by Country and Product Type')
plt.xlabel('Sales (in thousands)')
plt.ylabel('Quantity Sold')
plt.legend(title='Product Type')
plt.grid(True)

# Annotate each point with the country name
for i in range(df.shape[0]):
    plt.annotate(df['Country'][i], (df['Sales'][i], df['Quantity'][i]))

# Show plot
plt.show()
