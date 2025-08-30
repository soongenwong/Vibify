from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import sys
import shutil
import tempfile
from pathlib import Path
import json
from typing import Optional

# Add the src directory to the Python path to import music_analyzer
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from music_analyzer import MusicAnalyzer, MusicRecommendationEngine

app = FastAPI(title="Vibify Music Analysis API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React/Vite dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the music analyzer and recommendation engine
music_analyzer = MusicAnalyzer()
recommendation_engine = MusicRecommendationEngine(openai_api_key=os.getenv("OPENAI_API_KEY"))

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Vibify Music Analysis API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "api_key_configured": bool(os.getenv("OPENAI_API_KEY"))}

@app.post("/analyze")
async def analyze_music(file: UploadFile = File(...)):
    """
    Analyze an uploaded music file and extract musical features
    """
    # Validate file type
    allowed_extensions = {'.mp3', '.wav', '.flac', '.m4a', '.ogg'}
    file_extension = Path(file.filename).suffix.lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Create temporary file to store the upload
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
        try:
            # Copy uploaded file to temporary location
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name
            
            # Analyze the audio file
            features = music_analyzer.extract_music_features(temp_file_path)
            
            if features is None:
                raise HTTPException(status_code=500, detail="Failed to analyze audio file")
            
            if features.get("error"):
                raise HTTPException(status_code=400, detail=f"Analysis error: {features['error']}")
            
            # Add metadata
            analysis_result = {
                "filename": file.filename,
                "file_size": file.size,
                "features": features,
                "status": "success"
            }
            
            return analysis_result
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
        
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

@app.post("/recommend")
async def get_recommendations(file: UploadFile = File(...), song_name: Optional[str] = None):
    """
    Analyze music file and get song recommendations
    """
    # Validate file type
    allowed_extensions = {'.mp3', '.wav', '.flac', '.m4a', '.ogg'}
    file_extension = Path(file.filename).suffix.lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Create temporary file to store the upload
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
        try:
            # Copy uploaded file to temporary location
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name
            
            # Analyze the audio file
            features = music_analyzer.extract_music_features(temp_file_path)
            
            if features is None:
                raise HTTPException(status_code=500, detail="Failed to analyze audio file")
            
            if features.get("error"):
                raise HTTPException(status_code=400, detail=f"Analysis error: {features['error']}")
            
            # Get recommendations
            track_name = song_name or file.filename
            recommendations = recommendation_engine.get_recommendations(features, track_name)
            
            result = {
                "filename": file.filename,
                "song_name": track_name,
                "features": features,
                "recommendations": recommendations,
                "status": "success"
            }
            
            return result
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
        
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

@app.post("/recommend-from-features")
async def recommend_from_features(features: dict, song_name: Optional[str] = None):
    """
    Get recommendations from pre-analyzed features
    """
    try:
        recommendations = recommendation_engine.get_recommendations(features, song_name)
        
        return {
            "song_name": song_name,
            "recommendations": recommendations,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
