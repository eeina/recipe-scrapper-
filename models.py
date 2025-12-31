from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class ImageInfo(BaseModel):
    """Image information model"""

    url: str = Field(
        ..., description="Image URL (S3 URL if uploaded, otherwise original)"
    )
    key: Optional[str] = Field(None, description="S3 key if uploaded to S3")


class RecipeResponse(BaseModel):
    """Standardized recipe data model"""

    title: str = Field(..., description="The title of the recipe")
    description: str = Field(..., description="A description of the recipe")
    prep_time: int = Field(..., description="Preparation time in minutes", ge=0)
    cook_time: int = Field(..., description="Cooking time in minutes", ge=0)
    total_time: int = Field(..., description="Total time required in minutes", ge=0)
    yields: int = Field(
        ..., description="Yield or number of servings (0 if not specified)", ge=0
    )
    ingredients: List[str] = Field(..., description="List of ingredients")
    instructions: List[str] = Field(..., description="List of cooking instructions")
    image: ImageInfo = Field(..., description="Image information with URL and S3 key")
    url: str = Field(..., description="Original recipe URL")
    host: str = Field(..., description="Website host name")


class SuccessResponse(BaseModel):
    """Successful response model"""

    success: bool = Field(
        ..., example=True, description="Indicates if the request was successful"
    )
    source: str = Field(
        ..., description="Source method used: recipe-scraper, json-ld, or gemini"
    )
    processing_time: float = Field(
        ..., description="Time taken to process the request in seconds"
    )
    data: RecipeResponse = Field(..., description="The extracted recipe data")


class ErrorResponse(BaseModel):
    """Error response model"""

    success: bool = Field(
        ..., example=False, description="Indicates if the request was successful"
    )
    message: str = Field(..., description="Error message describing what went wrong")
    error_type: str = Field(..., description="Type of error that occurred")


class HealthResponse(BaseModel):
    """Health check response model"""

    status: str = Field(..., example="healthy", description="API status")
    timestamp: float = Field(..., description="Current server timestamp")
    gemini_configured: bool = Field(..., description="Whether Gemini API is configured")
    endpoints: Dict[str, str] = Field(..., description="Available API endpoints")
