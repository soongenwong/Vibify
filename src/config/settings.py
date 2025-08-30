"""
Configuration Settings

Central configuration management for the Vibify application.
"""

import os
from pathlib import Path
from typing import Optional


class Settings:
    """Application configuration settings"""
    
    # Project paths
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    SRC_DIR = PROJECT_ROOT / "src"
    DATA_DIR = PROJECT_ROOT / "data"
    INPUT_DIR = DATA_DIR / "input"
    OUTPUT_DIR = DATA_DIR / "output"
    
    # API Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_MAX_TOKENS: int = 1500
    OPENAI_TEMPERATURE: float = 0.7
    
    # Analysis Configuration
    SUPPORTED_AUDIO_FORMATS = {'.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg', '.wma'}
    DEFAULT_AUDIO_FILE = "hate-to-love.mp3"
    
    # Output Configuration
    ANALYSIS_OUTPUT_FILE = "music_analysis.json"
    RECOMMENDATIONS_OUTPUT_FILE = "song_recommendations.txt"
    
    # Logging Configuration
    LOG_LEVEL = "INFO"
    VERBOSE_OUTPUT = True
    
    @classmethod
    def ensure_directories(cls) -> None:
        """Ensure all required directories exist"""
        directories = [cls.DATA_DIR, cls.INPUT_DIR, cls.OUTPUT_DIR]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_input_path(cls, filename: str) -> Path:
        """Get full path for input file"""
        return cls.INPUT_DIR / filename
    
    @classmethod
    def get_output_path(cls, filename: str) -> Path:
        """Get full path for output file"""
        return cls.OUTPUT_DIR / filename
    
    @classmethod
    def validate_api_key(cls) -> bool:
        """Check if OpenAI API key is configured"""
        return cls.OPENAI_API_KEY is not None and len(cls.OPENAI_API_KEY.strip()) > 0
    
    @classmethod
    def get_analysis_output_path(cls, audio_filename: str) -> Path:
        """Get output path for analysis results"""
        safe_name = cls._get_safe_filename(audio_filename)
        return cls.OUTPUT_DIR / f"{safe_name}_analysis.json"
    
    @classmethod
    def get_recommendations_output_path(cls, audio_filename: str) -> Path:
        """Get output path for recommendations"""
        safe_name = cls._get_safe_filename(audio_filename)
        return cls.OUTPUT_DIR / f"{safe_name}_recommendations.txt"
    
    @classmethod
    def _get_safe_filename(cls, original_name: str) -> str:
        """Convert filename to safe format for output files"""
        name = Path(original_name).stem
        safe_name = "".join(c if c.isalnum() or c in "._-" else "_" for c in name)
        return safe_name