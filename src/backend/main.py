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
import re
from typing import List
import json

# Add the src directory to the Python path to import music_analyzer
# sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.analyzer import MusicAnalyzer
from src.core.recommender import MusicRecommendationEngine
from src.utils.file_utils import (
    validate_audio_file,
    save_analysis_results,
    save_recommendations,
)
from src.config.settings import Settings


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

def _split_title_artist(s: str) -> str:
    s = s.strip().strip('"\''"“”‘’")
    for sep in [" - ", " — ", " – ", " by "]:
        if sep in s:
            return s.split(sep, 1)[0].strip().strip('"\''"“”‘’")
    return s

def _parse_top5_from_text(text: str, k: int = 5) -> List[str]:
    # 1) Try JSON
    try:
        data = json.loads(text)
        items = []
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            for key in ("recommendations", "songs", "top", "top_5", "result", "titles"):
                if key in data and isinstance(data[key], list):
                    items = data[key]; break
        if items:
            seen, out = set(), []
            for x in items:
                t = _split_title_artist(str(x))
                if t and t.lower() not in seen:
                    out.append(t); seen.add(t.lower())
            return out[:k]
    except Exception:
        pass
    # 2) Parse bullets/numbered/freeform
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    cands = []
    for ln in lines:
        m = re.match(r"^\s*(?:\d+[\).:\-]\s*|[\-\*\•]\s+)(.+)$", ln)
        if m:
            cands.append(_split_title_artist(m.group(1)))
        else:
            qm = re.match(r'^\s*["“](.+?)["”](?:\s*[—–-]\s*.+)?$', ln)
            if qm:
                cands.append(_split_title_artist(qm.group(1)))
    if not cands:
        for ln in lines:
            if any(sep in ln for sep in [" - ", " — ", " – ", " by "]):
                cands.append(_split_title_artist(ln))
    seen, cleaned = set(), []
    for c in cands:
        c = re.sub(r"\s+\(\d{4}\)$", "", c).strip()
        if c and c.lower() not in seen:
            cleaned.append(c); seen.add(c.lower())
    if not cleaned:
        for ln in lines:
            if len(ln.split()) >= 2 and not ln.lower().startswith(("step", "analysis", "music recommendations")):
                cleaned.append(_split_title_artist(ln))
            if len(cleaned) >= k:
                break
    return cleaned[:k]

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

# --- add this new route anywhere after your other @app.* routes ---

@app.get("/recommendations")
async def recommendations_default():
    """
    Run the full pipeline using the default audio (no upload) and return top-5 song names.
    """
    Settings.ensure_directories()

    audio_path = Settings.get_input_path(Settings.DEFAULT_AUDIO_FILE)
    if not audio_path.exists():
        raise HTTPException(
            status_code=400,
            detail=f"Default audio not found at: {audio_path}. "
                   f"Place '{Settings.DEFAULT_AUDIO_FILE}' in data/input/."
        )
    if not validate_audio_file(audio_path):
        raise HTTPException(status_code=400, detail="Invalid or unsupported audio file.")

    features = music_analyzer.extract_music_features(str(audio_path))
    if features is None or features.get("error"):
        raise HTTPException(status_code=500, detail="Failed to extract features from audio file.")

    analysis_path = Settings.get_analysis_output_path(audio_path.name)
    save_analysis_results(features, str(analysis_path))

    song_name = Path(audio_path).stem.replace("_", " ").replace("-", " ").title()
    recommendations_text = recommendation_engine.get_recommendations(features, song_name)

    recommendations_path = Settings.get_recommendations_output_path(audio_path.name)
    save_recommendations(recommendations_text, str(recommendations_path), str(audio_path))

    top5 = _parse_top5_from_text(recommendations_text, k=5)

    return {
        "songs": top5,
        "raw_text": recommendations_text,
        "analysis_path": str(analysis_path),
        "recommendations_path": str(recommendations_path),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
