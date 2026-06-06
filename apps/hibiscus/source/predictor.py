import tensorflow as tf
import numpy as np
from PIL import Image

# Load model ONCE
from .model import load_model



CLASSES =[
'Mild Edge Damage' ,
'1',
'2',
'Senescent',
'4',
'5' ,
'6',
'Healthy',
]

from tensorflow.keras.applications.resnet50 import preprocess_input

MODEL = load_model()

def preprocess(image_file):
    img = Image.open(image_file).convert("RGB")
    img = img.resize((224, 224))
    arr = np.array(img, dtype=np.float32)
    arr = np.expand_dims(arr, axis=0)
    arr = preprocess_input(arr)  # for ResNet 
    return arr

def predict(image_file):

    img = preprocess(image_file)
    
    if MODEL is None:
        return {
            "error": "Model could not be loaded."
        }

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