# src/__init__.py
"""
Vibify - AI-Powered Music Recommendation System
"""

__version__ = "1.0.0"
__author__ = "Vibify Team"
__description__ = "AI-powered music recommendation system using musical DNA analysis"

# src/core/__init__.py
"""
Core music analysis and recommendation modules
"""

from .analyzer import MusicAnalyzer
from .recommender import MusicRecommendationEngine

__all__ = ['MusicAnalyzer', 'MusicRecommendationEngine']

# src/utils/__init__.py
"""
Utility functions for file handling and music processing
"""

from .file_utils import (
    validate_audio_file,
    find_audio_files,
    save_analysis_results,
    save_recommendations
)
from .music_utils import (
    format_pitch_classes,
    format_intervals,
    midi_to_note_name,
    categorize_tempo
)

__all__ = [
    'validate_audio_file',
    'find_audio_files', 
    'save_analysis_results',
    'save_recommendations',
    'format_pitch_classes',
    'format_intervals',
    'midi_to_note_name',
    'categorize_tempo'
]

# src/config/__init__.py
"""
Configuration management
"""

from .settings import Settings

__all__ = ['Settings']

# tests/__init__.py
"""
Test suite for Vibify
"""