import tensorflow as tf

def load_model():
    
    MODEL = tf.keras.models.load_model("apps\zucchini\source\Zucchini.h5", compile=False)  
    
    print(MODEL.summary())
    return MODEL
