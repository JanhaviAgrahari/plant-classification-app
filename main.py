from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
from sqlalchemy import text
from ml.model import load_model, classify_image
import shutil
import os
import logging
from pathlib import Path
from typing import List
import schemas

app = FastAPI()

# ----------------------------------------------------------------------------
# Logging configuration
# ----------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("plant_app")

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
    logger.info(f"Loading classification model from: {model_path}")
    model = load_model(model_path)
    logger.info("Model loaded successfully")
except Exception as e:
    logger.warning(f"Could not load model: {e}")
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
async def upload_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    logger.info(f"[UPLOAD] Received file: {file.filename}")
    
    # Create uploads directory if it doesn't exist
    upload_folder = "static/uploads/"
    os.makedirs(upload_folder, exist_ok=True)
    safe_filename = file.filename if file.filename is not None else "uploaded_file"
    file_location = os.path.join(upload_folder, safe_filename)
    logger.debug(f"Saving to: {file_location}")
    
    # Save the uploaded file
    try:
        # Read file content
        contents = await file.read()
        
        # Write content to new file
        with open(file_location, "wb") as f:
            f.write(contents)
            logger.info(f"File saved successfully, size: {len(contents)} bytes")
            # Reset file position for potential further operations
            await file.seek(0)
    except Exception as e:
        logger.error(f"Error saving file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
    
    # Handle classification
    try:
        if model:
            logger.info("Running model classification")
            prediction_result = classify_image(file_location, model)
            logger.debug(f"Raw prediction result: {prediction_result}")

            # Check if the image contains a plant
            if prediction_result.get("is_plant"):
                class_name = prediction_result.get("class_name", "<unknown>")
                confidence = prediction_result.get("confidence", 0.0)
                logger.info(f"Plant detected -> class: {class_name} | confidence: {confidence:.4f}")
            else:
                class_name = "Not a recognized plant"
                confidence = prediction_result.get("confidence", 0.0)
                logger.info(f"Image not recognized as plant | confidence: {confidence:.4f}")
        else:
            logger.warning("No model available, using fallback classification")
            prediction_result = {}
            class_name = "Unknown (model not available)"
            confidence = 0.0

        # ------------------------------------------------------------------
        # Fetch plant info from DB if we have a valid plant class
        # ------------------------------------------------------------------
        plant_record = None
        if model and prediction_result.get("is_plant") and class_name not in ["Not a recognized plant", "<unknown>"]:
            # Normalize class name for DB lookup (case-insensitive, strip spaces)
            normalized = class_name.strip()
            logger.debug(f"Looking up plant in DB: '{normalized}'")
            try:
                plant_record = (
                    db.query(models.Plant)
                    .filter(models.Plant.name.ilike(normalized))
                    .first()
                )
                if not plant_record:
                    # Try replacing underscores with spaces if needed
                    alt = normalized.replace("_", " ")
                    if alt != normalized:
                        logger.debug(f"Retry lookup with alt form: '{alt}'")
                        plant_record = (
                            db.query(models.Plant)
                            .filter(models.Plant.name.ilike(alt))
                            .first()
                        )
                if plant_record:
                    logger.info(
                        f"Plant info fetched: id={plant_record.id}, scientific_name={plant_record.scientific_name}"
                    )
                else:
                    logger.warning(f"No plant info found in DB for '{class_name}'")
            except Exception as db_e:
                logger.error(f"Database lookup error for '{class_name}': {db_e}")

        plant_payload = None
        if plant_record:
            plant_payload = {
                "id": plant_record.id,
                "name": plant_record.name,
                "scientific_name": plant_record.scientific_name,
                "family": plant_record.family,
                "origin": plant_record.origin,
                "description": plant_record.description,
                "uses": plant_record.uses,
                "image_url": plant_record.image_url,
            }
            logger.debug(f"Plant payload prepared: {plant_payload}")
            # Explicit console print for terminal visibility
            print(f"[PLANT_INFO] {plant_payload}")
        else:
            print(f"[PLANT_INFO] No database record found for classified name: {class_name}")

        result = {
            "filename": file.filename,
            "prediction": {
                "class_name": class_name,
                "confidence": confidence,
                "is_plant": prediction_result.get("is_plant", False) if model else False,
            },
            "plant_info": plant_payload,
        }
        logger.info("Returning response for upload-image request")
        logger.debug(f"Full response: {result}")
        print(f"[RESULT] {result}")
        return result
    except Exception as e:
        logger.exception(f"Classification flow error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Classification error: {str(e)}")

# Add this endpoint for testing basic upload functionality
@app.post("/test-upload/")
async def test_upload(file: UploadFile = File(...)):
    print(f"Test upload received: {file.filename}")
    return {"filename": file.filename, "status": "received"}

@app.get("/test-form", response_class=HTMLResponse)
async def test_form(request: Request):
    return templates.TemplateResponse("test-upload.html", {"request": request})