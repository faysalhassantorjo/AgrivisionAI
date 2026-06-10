# model.py
import tensorflow as tf
import os

def load_model():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    MODEL_PATH = os.path.join(BASE_DIR, "Papaya.h5")
    if not os.path.exists(MODEL_PATH):
        print(f"Model not found at: {MODEL_PATH}")
        return None
    return tf.keras.models.load_model(MODEL_PATH, compile=False)