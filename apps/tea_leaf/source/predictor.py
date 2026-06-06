import tensorflow as tf
import numpy as np
from PIL import Image

# Load model ONCE
from .model import load_model



CLASSES = ["Healthy", "Red Rust", "Algal Spot", "Anthracnose", "Brown Blight"]



def preprocess(image_file):
    img = Image.open(image_file).convert("RGB")
    img = img.resize((224, 224))
    arr = np.array(img, dtype=np.float32)
    arr = np.expand_dims(arr, axis=0)
    
    arr = tf.keras.applications.mobilenet_v2.preprocess_input(arr)
    return arr


def predict(image_file):

    img = preprocess(image_file)

    MODEL = load_model()

    preds = MODEL.predict(img)
    
    print('Raw preds: ', preds)
    print('Preds sum: ', np.sum(preds))  
    print('All class scores:')
    for i, (cls, score) in enumerate(zip(CLASSES, preds[0])):
        print(f"  {i}: {cls} → {score:.6f}")

    idx = np.argmax(preds)

    confidence = float(np.max(preds) * 100)

    return {
        "class": CLASSES[idx],
        "confidence": round(confidence, 2)
    }