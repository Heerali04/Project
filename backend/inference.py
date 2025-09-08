from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
import pandas as pd
import joblib

# --- Load BioBERT for NER ---
tokenizer = AutoTokenizer.from_pretrained("d4data/biobert_ner")
model = AutoModelForTokenClassification.from_pretrained("d4data/biobert_ner")
ner_pipeline = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")

# --- Load trained XGBoost model ---
xgb_model = joblib.load("xgboost_model.pkl")
symptom_list = joblib.load("symptom_list.pkl")  # same order as training

# --- Symptom Extraction ---
def extract_symptoms(text, symptom_list):
    entities = ner_pipeline(text)
    found = [e['word'].lower() for e in entities]
    return {sym: 1 if sym in found else 0 for sym in symptom_list}

# --- Prediction ---
def predict_disease(user_text):
    vec = extract_symptoms(user_text, symptom_list)
    X = pd.DataFrame([vec])
    return xgb_model.predict(X)[0]

# Example
print(predict_disease("I have fever, vomiting and headache"))
