import os
import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from app.config import Config

# Check if model exists, if not create a simple one
def get_or_create_model():
    model_path = Config.SIGNATURE_MODEL_PATH
    
    if os.path.exists(model_path):
        return load_model(model_path)
    else:
        # Create a simple CNN model for signature verification
        model = tf.keras.Sequential([
            tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(150, 150, 3)),
            tf.keras.layers.MaxPooling2D(2, 2),
            tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
            tf.keras.layers.MaxPooling2D(2, 2),
            tf.keras.layers.Conv2D(128, (3, 3), activation='relu'),
            tf.keras.layers.MaxPooling2D(2, 2),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(512, activation='relu'),
            tf.keras.layers.Dense(1, activation='sigmoid')
        ])
        
        model.compile(optimizer='adam',
                     loss='binary_crossentropy',
                     metrics=['accuracy'])
        
        # Save the model
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        model.save(model_path)
        
        return model

def verify_signature(signature_path):
    """
    Verify if a signature is authentic or potentially forged
    
    In a real implementation, this would use a trained model.
    For this example, we'll use a simple heuristic based on image properties.
    """
    try:
        # Load the signature image
        img = Image.open(signature_path)
        
        # Convert to grayscale
        img = img.convert('L')
        
        # Convert to numpy array
        img_array = np.array(img)
        
        # Simple heuristic: check if the signature has enough black pixels
        # and if the distribution of pixels is not too uniform (which might indicate a forgery)
        black_pixels = np.sum(img_array < 128)
        total_pixels = img_array.size
        black_ratio = black_pixels / total_pixels
        
        # Calculate standard deviation of pixel values as a measure of complexity
        std_dev = np.std(img_array)
        
        # In a real system, we would use the model to predict
        # model = get_or_create_model()
        # img = image.load_img(signature_path, target_size=(150, 150))
        # img_array = image.img_to_array(img)
        # img_array = np.expand_dims(img_array, axis=0)
        # prediction = model.predict(img_array)[0][0]
        
        # For this example, use our heuristics
        if black_ratio < 0.01 or std_dev < 20:
            return 'suspicious'  # Too few black pixels or too uniform
        else:
            return 'verified'
            
    except Exception as e:
        print(f"Error verifying signature: {e}")
        return 'unsigned'  # Default to unsigned if there's an error
