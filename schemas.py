from pydantic import BaseModel
from typing import Optional


class PlantBase(BaseModel):
    id: int
    name: str
    scientific_name: str
    family: Optional[str] = None
    origin: Optional[str] = None
    description: Optional[str] = None
    uses: Optional[str] = None
    image_url: Optional[str] = None

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
