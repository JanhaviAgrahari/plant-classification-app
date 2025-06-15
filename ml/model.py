import tensorflow as tf
import numpy as np
import os


def load_model(model_path):
    """Load the TensorFlow/Keras model from the given path."""
    try:
        # This works with both H5 files and SavedModel directories
        model = tf.keras.models.load_model(model_path)
        print(f"Successfully loaded model from {model_path}")
        return model
    except Exception as e:
        print(f"Error loading model: {e}")
        print(f"Checking if path exists: {os.path.exists(model_path)}")
        raise


def preprocess_image(img_path):
    """Preprocess an image file for classification."""
    # Load the image using updated function names
    img = tf.keras.utils.load_img(img_path, target_size=(224, 224))
    img_array = tf.keras.utils.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array /= 255.0  # Normalize the image
    return img_array


def classify_image(img_path, model):
    """Classify an image using the provided model and return prediction with confidence."""
    try:
        print(f"Starting classification for: {img_path}")
        # Preprocess the image
        processed_image = preprocess_image(img_path)

        # Make predictions
        print("Making predictions...")
        predictions = model.predict(processed_image)
        print(f"Raw prediction shape: {predictions.shape}")

        # Get the class with highest probability
        predicted_class = np.argmax(predictions, axis=1)[0]

        # Get the actual confidence (probability) for the predicted class
        confidence = float(predictions[0][predicted_class])
        print(f"Predicted class: {predicted_class}, confidence: {confidence}")

        # Class name mapping - using the provided class indices
        class_names = {
            0: "aloe vera",
            1: "banana",
            2: "bilimbi",
            3: "cantaloupe",
            4: "cassava",
            5: "coconut",
            6: "corn",
            7: "cucumber",
            8: "curcuma",
            9: "eggplant",
            10: "galangal",
            11: "ginger",
            12: "guava",
            13: "kale",
            14: "longbeans",
            15: "mango",
            16: "melon",
            17: "orange",
            18: "paddy",
            19: "papaya",
            20: "pepper chili",
            21: "pineapple",
            22: "pomelo",
            23: "shallot",
            24: "soybeans",
            25: "spinach",
            26: "sweet potatoes",
            27: "tobacco",
            28: "waterapple",
            29: "watermelon",
        }

        # Format class name nicely (capitalize first letter of each word)
        class_name = class_names.get(
            predicted_class, f"Unknown Plant ({predicted_class})"
        )
        formatted_class_name = " ".join(
            word.capitalize() for word in class_name.split()
        )

        print(f"Formatted class name: {formatted_class_name}")

        # Determine if this is actually a plant (confidence threshold)
        is_plant = confidence >= 0.70  # 70% confidence threshold

        return {
            "class_id": int(predicted_class),
            "class_name": formatted_class_name,
            "raw_class_name": class_name,
            "confidence": confidence,
            "is_plant": is_plant,
        }
    except Exception as e:
        print(f"Error in classification: {e}")
        raise
