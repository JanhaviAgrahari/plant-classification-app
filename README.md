# Plant Classification App

## Overview
The Plant Classification App is a FastAPI application that allows users to upload images of plants for classification. The application utilizes a pre-trained Keras model to predict the species of the plant based on the uploaded image.

## Project Structure
```
plant_classification_app
├── main.py                  # Entry point of the FastAPI application
├── database.py              # Database connection setup using SQLAlchemy
├── models.py                # SQLAlchemy models for the application
├── schemas.py               # Pydantic schemas for data validation
├── ml
│   ├── model.py             # Logic for loading the model and making predictions
│   ├── preprocessing.py      # Functions for preprocessing images
│   └── Plant_Classification_Model.h5  # Trained Keras model file
├── static
│   ├── css
│   │   └── styles.css       # CSS styles for the frontend
│   ├── js
│   │   └── app.js           # JavaScript code for frontend interactions
│   └── uploads
│       └── .gitkeep         # Empty file to track uploads directory in Git
├── templates
│   └── index.html           # HTML template for the frontend
├── requirements.txt         # List of dependencies for the project
└── README.md                # Documentation for the project
```

## Setup Instructions
1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd plant_classification_app
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   uvicorn main:app --reload
   ```

5. **Access the application**:
   Open your web browser and go to `http://127.0.0.1:8000`.

## Usage
- Upload an image of a plant using the provided form.
- The application will process the image and return the predicted plant species.

## Dependencies
- FastAPI
- SQLAlchemy
- TensorFlow
- Pydantic
- Uvicorn

## License
This project is licensed under the MIT License.