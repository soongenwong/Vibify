# tests/test_utils.py
"""
Unit tests for utility functions
"""

import pytest
import tempfile
import json
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from utils.file_utils import (
    validate_audio_file, 
    find_audio_files, 
    save_analysis_results,
    save_recommendations,
    get_safe_filename
)
from utils.music_utils import (
    format_pitch_classes,
    format_intervals,
    midi_to_note_name,
    categorize_tempo,
    get_key_signature_hints,
    analyze_musical_complexity
)


class TestFileUtils:
    
    def test_validate_audio_file_nonexistent(self):
        """Test validation of non-existent file"""
        assert not validate_audio_file("nonexistent.mp3")
    
    def test_validate_audio_file_unsupported_format(self, tmp_path):
        """Test validation of unsupported file format"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        
        assert not validate_audio_file(str(test_file))
    
    def test_validate_audio_file_supported_format(self, tmp_path):
        """Test validation of supported file format"""
        test_file = tmp_path / "test.mp3"
        test_file.write_bytes(b"fake mp3 content")
        
        assert validate_audio_file(str(test_file))
    
    def test_find_audio_files(self, tmp_path):
        """Test finding audio files in directory"""
        # Create test files
        (tmp_path / "song1.mp3").write_bytes(b"test")
        (tmp_path / "song2.wav").write_bytes(b"test")
        (tmp_path / "not_audio.txt").write_text("test")
        
        audio_files = find_audio_files(str(tmp_path))
        
        assert len(audio_files) == 2
        assert any("song1.mp3" in f for f in audio_files)
        assert any("song2.wav" in f for f in audio_files)
    
    def test_save_analysis_results(self, tmp_path):
        """Test saving analysis results"""
        features = {
            "pitch_range": {"min": 60.0, "max": 72.0},
            "rhythm": {"total_notes": 100}
        }
        
        output_path = tmp_path / "test_analysis.json"
        
        assert save_analysis_results(features, str(output_path))
        assert output_path.exists()
        
        # Verify content
        with open(output_path) as f:
            loaded = json.load(f)
        
        assert loaded["pitch_range"]["min"] == 60.0
        assert loaded["rhythm"]["total_notes"] == 100
    
    def test_save_recommendations(self, tmp_path):
        """Test saving recommendations"""
        recommendations = "1. Song A - Similar tempo\n2. Song B - Similar key"
        output_path = tmp_path / "test_recommendations.txt"
        audio_file = "test_song.mp3"
        
        assert save_recommendations(recommendations, str(output_path), audio_file)
        assert output_path.exists()
        
        # Verify content
        content = output_path.read_text()
        assert "test_song.mp3" in content
        assert recommendations in content
    
    def test_get_safe_filename(self):
        """Test safe filename generation"""
        assert get_safe_filename("song with spaces.mp3") == "song_with_spaces"
        assert get_safe_filename("song@#$%.wav") == "song____"
        assert get_safe_filename("normal-song_123.flac") == "normal-song_123"


class TestMusicUtils:
    
    def test_format_pitch_classes(self):
        """Test pitch class formatting"""
        pitch_classes = {"C": 20, "G": 15, "F": 10, "D": 5}
        formatted = format_pitch_classes(pitch_classes)
        
        assert "C(20)" in formatted
        assert "G(15)" in formatted
        # Should show top 4
        assert formatted.count("(") == 4
    
    def test_format_pitch_classes_empty(self):
        """Test pitch class formatting with empty data"""
        assert format_pitch_classes({}) == "No pitch data"
    
    def test_format_intervals(self):
        """Test interval formatting"""
        intervals = {2: 10, 4: 8, 5: 6, 1: 3}
        formatted = format_intervals(intervals)
        
        assert "2(10)" in formatted
        assert "4(8)" in formatted
        # Should show top 3
        assert formatted.count("(") == 3
    
    def test_format_intervals_empty(self):
        """Test interval formatting with empty data"""
        assert format_intervals({}) == "No clear patterns"
    
    def test_midi_to_note_name(self):
        """Test MIDI to note name conversion"""
        assert midi_to_note_name(60) == "C4"
        assert midi_to_note_name(69) == "A4"
        assert midi_to_note_name(72) == "C5"
        assert midi_to_note_name(61) == "C#4"
    
    def test_categorize_tempo(self):
        """Test tempo categorization"""
        assert "Very Slow" in categorize_tempo(50)
        assert "Slow" in categorize_tempo(70)
        assert "Moderate" in categorize_tempo(90)
        assert "Medium" in categorize_tempo(110)
        assert "Fast" in categorize_tempo(130)
        assert "Very Fast" in categorize_tempo(160)
        assert "Extremely Fast" in categorize_tempo(200)
    
    def test_get_key_signature_hints(self):
        """Test key signature analysis"""
        # C major scale notes
        c_major_notes = {"C": 10, "D": 8, "E": 7, "F": 6, "G": 9, "A": 5, "B": 4}
        hints = get_key_signature_hints(c_major_notes)
        
        assert "C" in hints  # Should detect C major
        assert len(hints) <= 3  # Max 3 suggestions
    
    def test_get_key_signature_hints_empty(self):
        """Test key signature analysis with empty data"""
        hints = get_key_signature_hints({})
        assert hints == ["Unknown"]
    
    def test_analyze_musical_complexity(self):
        """Test musical complexity analysis"""
        features = {
            'pitch_range': {'std': 12.0},  # High pitch variation
            'rhythm': {'note_density': 6.0},  # High note density
            'dynamics': {'velocity_std': 25.0}  # High dynamic range
        }
        
        complexity = analyze_musical_complexity(features)
        
        assert "High" in complexity['melody']
        assert "High" in complexity['rhythm']
        assert "High" in complexity['dynamics']
    
    def test_analyze_musical_complexity_simple(self):
        """Test musical complexity analysis for simple music"""
        features = {
            'pitch_range': {'std': 3.0},  # Low pitch variation
            'rhythm': {'note_density': 1.0},  # Low note density
            'dynamics': {'velocity_std': 5.0}  # Low dynamic range
        }
        
        complexity = analyze_musical_complexity(features)
        
        assert "Low" in complexity['melody']
        assert "Low" in complexity['rhythm']
        assert "Low" in complexity['dynamics']