import tensorflow as tf

def load_model():
    
    MODEL = tf.keras.models.load_model("apps/tea_leaf/source/tea_leaf_model.h5", compile=False)  
    
    print(MODEL.summary())
    return MODEL
