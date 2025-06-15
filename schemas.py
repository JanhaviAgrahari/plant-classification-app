from pydantic import BaseModel

class PlantBase(BaseModel):
    id: int
    name: str
    scientific_name: str
    family: str = None
    origin: str = None
    description: str = None
    uses: str = None
    image_url: str = None
    
    class Config:
        orm_mode = True

class PlantClassificationResult(BaseModel):
    class_name: str
    confidence: float

class UploadImageResponse(BaseModel):
    filename: str
    prediction: PlantClassificationResult

class ErrorResponse(BaseModel):
    detail: str