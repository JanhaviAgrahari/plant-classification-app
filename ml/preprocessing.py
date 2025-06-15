from PIL import Image
import numpy as np


def preprocess_image(image_path: str, target_size=(224, 224)):
    """
    Load and preprocess the image for model prediction.

    Parameters:
    - image_path: str - Path to the image file.
    - target_size: tuple - Desired size for the image (width, height).

    Returns:
    - np.array - Preprocessed image ready for model input.
    """
    # Load the image
    image = Image.open(image_path)

    # Resize the image
    image = image.resize(target_size)

    # Convert the image to a numpy array
    image_array = np.array(image)

    # Normalize the image array
    image_array = image_array / 255.0

    # Expand dimensions to match model input shape
    image_array = np.expand_dims(image_array, axis=0)

    return image_array
