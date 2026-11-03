# custom.py
import tensorflow as tf

model = tf.keras.models.load_model(
    r"D:\ModelRun\apps\hibiscus\source\HibiscusandTea.h5",  # r"..." fixes backslashes
    compile=False
)

model.save(r"D:\ModelRun\apps\hibiscus\source\hibiscus_converted.keras")
print("Converted successfully. Output shape:", model.output_shape)