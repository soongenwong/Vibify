"""
File Utilities

Helper functions for file handling, validation, and path management.
"""

import os
import json
from pathlib import Path
from typing import List, Optional, Dict, Any


# Supported audio formats
SUPPORTED_AUDIO_FORMATS = {'.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg', '.wma'}


def validate_audio_file(file_path: str) -> bool:
    """
    Validate if the file exists and is a supported audio format
    
    Args:
        file_path: Path to the audio file
        
    Returns:
        True if valid, False otherwise
    """
    path = Path(file_path)
    
    if not path.exists():
        print(f"Error: File '{file_path}' does not exist")
        return False
    
    if path.suffix.lower() not in SUPPORTED_AUDIO_FORMATS:
        print(f"Error: Unsupported file format '{path.suffix}'")
        print(f"Supported formats: {', '.join(SUPPORTED_AUDIO_FORMATS)}")
        return False
    
    return True


def find_audio_files(directory: str) -> List[str]:
    """
    Find all audio files in a directory
    
    Args:
        directory: Directory path to search
        
    Returns:
        List of audio file paths
    """
    audio_files = []
    dir_path = Path(directory)
    
    if not dir_path.exists():
        return audio_files
    
    for file_path in dir_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_AUDIO_FORMATS:
            audio_files.append(str(file_path))
    
    return sorted(audio_files)


def save_analysis_results(features: Dict[str, Any], output_path: str) -> bool:
    """
    Save musical analysis results to JSON file
    
    Args:
        features: Musical features dictionary
        output_path: Path to save the JSON file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure output directory exists
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Convert any numpy types to native Python types for JSON serialization
        json_features = json.loads(json.dumps(features, default=str))
        
        with open(output_path, 'w') as f:
            json.dump(json_features, f, indent=2)
        
        print(f"Analysis saved to: {output_path}")
        return True
        
    except Exception as e:
        print(f"Error saving analysis: {e}")
        return False


def save_recommendations(recommendations: str, output_path: str, audio_file: str) -> bool:
    """
    Save recommendations to text file
    
    Args:
        recommendations: Recommendation text from LLM
        output_path: Path to save the text file
        audio_file: Original audio file name for reference
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure output directory exists
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w") as f:
            f.write(f"Music Recommendations for {Path(audio_file).name}\n")
            f.write("=" * 50 + "\n\n")
            f.write(recommendations)
        
        print(f"Recommendations saved to: {output_path}")
        return True
        
    except Exception as e:
        print(f"Error saving recommendations: {e}")
        return False


def load_analysis_results(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Load previously saved analysis results
    
    Args:
        file_path: Path to the JSON analysis file
        
    Returns:
        Loaded features dictionary or None if failed
    """
    try:
        with open(file_path, 'r') as f:
            features = json.load(f)
        return features
    except Exception as e:
        print(f"Error loading analysis: {e}")
        return None


def create_project_directories(base_path: str = ".") -> None:
    """
    Create the standard project directory structure
    
    Args:
        base_path: Base directory to create structure in
    """
    directories = [
        "data/input",
        "data/output",
        "src/core",
        "src/utils",
        "src/config",
        "tests",
        "examples"
    ]
    
    base = Path(base_path)
    
    for directory in directories:
        dir_path = base / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py files for Python packages
        if directory.startswith("src/"):
            init_file = dir_path / "__init__.py"
            if not init_file.exists():
                init_file.touch()
    
    print(f"Project directories created in: {base_path}")


def get_safe_filename(original_name: str) -> str:
    """
    Convert filename to safe format for output files
    
    Args:
        original_name: Original filename
        
    Returns:
        Safe filename for output
    """
    # Remove extension and replace problematic characters
    name = Path(original_name).stem
    safe_name = "".join(c if c.isalnum() or c in "._-" else "_" for c in name)
    return safe_name