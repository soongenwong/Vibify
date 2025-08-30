# src/backend/main.py
import asyncio
import json
import re
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- Your project imports (run uvicorn from project root) ---
from src.core.analyzer import MusicAnalyzer
from src.core.recommender import MusicRecommendationEngine
from src.utils.file_utils import validate_audio_file, save_analysis_results, save_recommendations
from src.config.settings import Settings


app = FastAPI(title="Vibify API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", "http://127.0.0.1:3000",
        "http://localhost:5173", "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RecommendationResponse(BaseModel):
    songs: List[str]
    raw_text: str
    analysis_path: Optional[str] = None
    recommendations_path: Optional[str] = None


def _split_title_artist(s: str) -> str:
    s = s.strip().strip('"\''"“”‘’")
    for sep in [" - ", " — ", " – ", " by "]:
        if sep in s:
            return s.split(sep, 1)[0].strip().strip('"\''"“”‘’")
    return s


def _parse_top5_from_text(text: str, k: int = 5) -> List[str]:
    # Try JSON
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
            out, seen = [], set()
            for x in items:
                t = _split_title_artist(str(x))
                if t and t.lower() not in seen:
                    out.append(t); seen.add(t.lower())
            return out[:k]
    except Exception:
        pass

    # Bullets / numbered
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


def _run_vibify_pipeline() -> RecommendationResponse:
    Settings.ensure_directories()

    audio_path = Settings.get_input_path(Settings.DEFAULT_AUDIO_FILE)
    if not audio_path.exists():
        raise HTTPException(
            status_code=400,
            detail=f"Default audio not found at {audio_path}. Place '{Settings.DEFAULT_AUDIO_FILE}' in data/input/."
        )

    if not validate_audio_file(audio_path):
        raise HTTPException(status_code=400, detail="Invalid or unsupported audio file.")

    analyzer = MusicAnalyzer()
    api_key = Settings.OPENAI_API_KEY if Settings.validate_api_key() else None
    recommender = MusicRecommendationEngine(openai_api_key=api_key)

    features = analyzer.extract_music_features(str(audio_path))
    if features is None:
        raise HTTPException(status_code=500, detail="Failed to extract features from audio file.")

    analysis_path = Settings.get_analysis_output_path(Path(audio_path).name)
    save_analysis_results(features, str(analysis_path))

    song_name = Path(audio_path).stem.replace("_", " ").replace("-", " ").title()
    recommendations_text = recommender.get_recommendations(features, song_name)

    recommendations_path = Settings.get_recommendations_output_path(Path(audio_path).name)
    save_recommendations(recommendations_text, str(recommendations_path), str(audio_path))

    top5 = _parse_top5_from_text(recommendations_text, k=5)

    return RecommendationResponse(
        songs=top5,
        raw_text=recommendations_text,
        analysis_path=str(analysis_path),
        recommendations_path=str(recommendations_path),
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/recommendations", response_model=RecommendationResponse)
async def get_recommendations():
    return await asyncio.to_thread(_run_vibify_pipeline)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.backend.main:app", host="127.0.0.1", port=8000, reload=True)
