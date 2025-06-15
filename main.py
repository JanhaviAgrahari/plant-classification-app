from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
from ml.model import load_model, classify_image
import shutil
import os
from pathlib import Path
from typing import List
import schemas

app = FastAPI()

# CORS middleware first
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Load the classification model
try:
    # Update path to your Keras SavedModel directory
    model_path = "ml/best_plant_classifier.keras"  # Directory containing the SavedModel
    model = load_model(model_path)
except Exception as e:
    print(f"Warning: Could not load model: {e}")
    model = None  # Proceed without model for now

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Root endpoint - serve the main.html template instead of index.html
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})

# Get all plants endpoint
@app.get("/plants", response_model=List[schemas.PlantBase])
def read_plants(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    plants = db.query(models.Plant).offset(skip).limit(limit).all()
    return plants

# Image upload and classification endpoint
@app.post("/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    print(f"Received file: {file.filename}")  # Debug print
    
    # Create uploads directory if it doesn't exist
    upload_folder = "static/uploads/"
    os.makedirs(upload_folder, exist_ok=True)
    file_location = os.path.join(upload_folder, file.filename)
    print(f"Saving to: {file_location}")
    
    # Save the uploaded file
    try:
        # Read file content
        contents = await file.read()
        
        # Write content to new file
        with open(file_location, "wb") as f:
            f.write(contents)
            
        print(f"File saved successfully, size: {len(contents)} bytes")
        
        # Reset file position for potential further operations
        await file.seek(0)
    except Exception as e:
        print(f"Error saving file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
    
    # Handle classification
    try:
        if model:
            print("Using model for classification")
            prediction_result = classify_image(file_location, model)
            
            # Check if the image contains a plant
            if prediction_result["is_plant"]:
                class_name = prediction_result["class_name"]
                confidence = prediction_result["confidence"]
                print(f"Plant detected! Classification: {class_name}, confidence: {confidence}")
            else:
                class_name = "Not a recognized plant"
                confidence = prediction_result["confidence"]
                print(f"Not a recognized plant. Confidence: {confidence}")
                
        else:
            print("No model available, using fallback classification")
            class_name = "Unknown (model not available)"
            confidence = 0.0
            
        result = {
            "filename": file.filename,
            "prediction": {
                "class_name": class_name,
                "confidence": confidence,
                "is_plant": prediction_result.get("is_plant", False) if model else False
            }
        }
        print(f"Returning result: {result}")
        return result
    except Exception as e:
        print(f"Classification error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Classification error: {str(e)}")

# Add this endpoint for testing basic upload functionality
@app.post("/test-upload/")
async def test_upload(file: UploadFile = File(...)):
    print(f"Test upload received: {file.filename}")
    return {"filename": file.filename, "status": "received"}

@app.get("/test-form", response_class=HTMLResponse)
async def test_form(request: Request):
    return templates.TemplateResponse("test-upload.html", {"request": request})