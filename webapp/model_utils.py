import fasttext
from config import MODEL_PATH

model = fasttext.load_model(MODEL_PATH)

def predict(text):
    return model.predict(text)
