"""
Music Analysis Module using Basic-Pitch

This module provides comprehensive music feature extraction from audio files
using Spotify's Basic-Pitch model for pitch detection and note transcription.
"""

import pandas as pd
import numpy as np
from basic_pitch.inference import predict
from typing import Dict, List, Optional, Tuple, Any


class MusicAnalyzer:
    """Main class for extracting musical features from audio files"""
    
    def __init__(self):
        """Initialize the music analyzer with Basic-Pitch model"""
        pass
        
    def extract_music_features(self, audio_path: str) -> Optional[Dict[str, Any]]:
        """
        Extract comprehensive music features from audio file
        
        Args:
            audio_path (str): Path to audio file (.mp3, .wav, .flac, etc.)
            
        Returns:
            dict: Musical features for LLM analysis, or None if failed
        """
        print(f"Analyzing {audio_path}...")
        
        try:
            # Run Basic-Pitch inference
            model_output, midi_data, note_events = predict(audio_path)
            
            # Convert note_events to proper format if needed
            if note_events and len(note_events) > 0:
                formatted_events = self._format_note_events(note_events)
                features = self._analyze_note_events(formatted_events)
                return features
            else:
                return {"error": "No notes detected"}
            
        except Exception as e:
            print(f"Error analyzing {audio_path}: {e}")
            return None
    
    def _format_note_events(self, note_events: List) -> List[Dict[str, float]]:
        """
        Format note events from Basic-Pitch into standardized dictionaries
        
        Args:
            note_events: Raw note events from Basic-Pitch
            
        Returns:
            List of formatted note event dictionaries
        """
        formatted_events = []
        
        for event in note_events:
            if isinstance(event, tuple):
                # Format: (start_time, end_time, pitch, velocity, confidence_data)
                formatted_events.append({
                    'start_time': float(event[0]),
                    'end_time': float(event[1]),
                    'duration': float(event[1] - event[0]),
                    'pitch': float(event[2]),
                    'velocity': float(event[3]),
                    'confidence': float(event[4]) if len(event) > 4 else 0.5
                })
            else:
                # Already in dict format
                formatted_events.append(event)
        
        return formatted_events
    
    def _analyze_note_events(self, note_events: List[Dict[str, float]]) -> Dict[str, Any]:
        """
        Analyze note events to extract musical characteristics
        
        Args:
            note_events: List of formatted note events
            
        Returns:
            Dictionary containing comprehensive musical features
        """
        if not note_events:
            return {"error": "No notes detected"}
        
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(note_events)
        
        # Calculate musical features
        features = {
            # Pitch characteristics
            "pitch_range": {
                "min": float(df['pitch'].min()),
                "max": float(df['pitch'].max()),
                "mean": float(df['pitch'].mean()),
                "std": float(df['pitch'].std())
            },
            
            # Rhythm characteristics
            "rhythm": {
                "total_notes": len(df),
                "avg_duration": float(df['duration'].mean()),
                "duration_std": float(df['duration'].std()),
                "note_density": len(df) / float(df['end_time'].max()) if df['end_time'].max() > 0 else 0
            },
            
            # Dynamics
            "dynamics": {
                "avg_velocity": float(df['velocity'].mean()),
                "velocity_range": float(df['velocity'].max() - df['velocity'].min()),
                "velocity_std": float(df['velocity'].std())
            },
            
            # Temporal features
            "temporal": {
                "song_duration": float(df['end_time'].max()),
                "onset_pattern": self._analyze_onset_pattern(df),
                "tempo_estimate": self._estimate_tempo(df)
            },
            
            # Musical intervals and harmony hints
            "harmony": {
                "pitch_classes": self._get_pitch_classes(df),
                "interval_distribution": self._analyze_intervals(df)
            }
        }
        
        return features
    
    def _analyze_onset_pattern(self, df: pd.DataFrame) -> List[float]:
        """
        Analyze rhythm patterns from note onsets
        
        Args:
            df: DataFrame containing note events
            
        Returns:
            List of most common rhythm patterns (inter-onset intervals)
        """
        onsets = sorted(df['start_time'].values)
        if len(onsets) < 2:
            return []
        
        # Calculate inter-onset intervals
        intervals = np.diff(onsets)
        
        # Find common rhythm patterns
        rounded_intervals = np.round(intervals, 2)
        unique, counts = np.unique(rounded_intervals, return_counts=True)
        
        # Return most common intervals (rhythm patterns)
        pattern_indices = np.argsort(counts)[-5:]  # Top 5 patterns
        common_patterns = unique[pattern_indices].tolist()
        
        return common_patterns
    
    def _estimate_tempo(self, df: pd.DataFrame) -> float:
        """
        Rough tempo estimation from note density
        
        Args:
            df: DataFrame containing note events
            
        Returns:
            Estimated BPM
        """
        if df['end_time'].max() == 0:
            return 0.0
        
        # Calculate notes per second, convert to approximate BPM
        notes_per_second = len(df) / df['end_time'].max()
        # Rough estimation: assume 4 notes per beat on average
        estimated_bpm = notes_per_second * 15  # 60 / 4 = 15
        
        return float(estimated_bpm)
    
    def _get_pitch_classes(self, df: pd.DataFrame) -> Dict[str, int]:
        """
        Get pitch class distribution (C, C#, D, etc.)
        
        Args:
            df: DataFrame containing note events
            
        Returns:
            Dictionary mapping note names to occurrence counts
        """
        pitch_classes = df['pitch'] % 12
        unique, counts = np.unique(pitch_classes, return_counts=True)
        
        # Convert to note names
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        pitch_class_dist = {}
        
        for pc, count in zip(unique, counts):
            pitch_class_dist[note_names[int(pc)]] = int(count)
            
        return pitch_class_dist
    
    def _analyze_intervals(self, df: pd.DataFrame) -> Dict[int, int]:
        """
        Analyze melodic intervals between consecutive notes
        
        Args:
            df: DataFrame containing note events
            
        Returns:
            Dictionary mapping intervals to occurrence counts
        """
        pitches = sorted(df['pitch'].values)
        if len(pitches) < 2:
            return {}
        
        intervals = np.diff(pitches)
        # Focus on intervals within an octave
        intervals = intervals[abs(intervals) <= 12]
        
        unique, counts = np.unique(intervals, return_counts=True)
        
        # Return most common intervals
        return dict(zip(unique.astype(int).tolist(), counts.astype(int).tolist()))