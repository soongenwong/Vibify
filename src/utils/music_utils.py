"""
Music Utilities

Helper functions for music theory, formatting, and data processing.
"""

from typing import Dict, List, Union


def format_pitch_classes(pitch_classes: Dict[str, int]) -> str:
    """
    Format pitch class distribution for readability
    
    Args:
        pitch_classes: Dictionary mapping note names to counts
        
    Returns:
        Formatted string showing top pitch classes
    """
    if not pitch_classes:
        return "No pitch data"
    
    sorted_pc = sorted(pitch_classes.items(), key=lambda x: x[1], reverse=True)
    return ", ".join([f"{note}({count})" for note, count in sorted_pc[:4]])


def format_intervals(intervals: Dict[int, int]) -> str:
    """
    Format interval distribution for readability
    
    Args:
        intervals: Dictionary mapping intervals to counts
        
    Returns:
        Formatted string showing common intervals
    """
    if not intervals:
        return "No clear patterns"
    
    sorted_intervals = sorted(intervals.items(), key=lambda x: x[1], reverse=True)
    return ", ".join([f"{interval}({count})" for interval, count in sorted_intervals[:3]])


def midi_to_note_name(midi_number: float) -> str:
    """
    Convert MIDI note number to note name with octave
    
    Args:
        midi_number: MIDI note number (0-127)
        
    Returns:
        Note name (e.g., "C4", "F#5")
    """
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = int(midi_number // 12) - 1
    note = note_names[int(midi_number % 12)]
    return f"{note}{octave}"


def get_key_signature_hints(pitch_classes: Dict[str, int]) -> List[str]:
    """
    Analyze pitch class distribution to suggest possible key signatures
    
    Args:
        pitch_classes: Dictionary mapping note names to counts
        
    Returns:
        List of likely key signatures
    """
    if not pitch_classes:
        return ["Unknown"]
    
    # Major scale patterns (relative frequency)
    major_patterns = {
        'C': ['C', 'D', 'E', 'F', 'G', 'A', 'B'],
        'G': ['G', 'A', 'B', 'C', 'D', 'E', 'F#'],
        'D': ['D', 'E', 'F#', 'G', 'A', 'B', 'C#'],
        'A': ['A', 'B', 'C#', 'D', 'E', 'F#', 'G#'],
        'E': ['E', 'F#', 'G#', 'A', 'B', 'C#', 'D#'],
        'F': ['F', 'G', 'A', 'A#', 'C', 'D', 'E'],
        'A#': ['A#', 'C', 'D', 'D#', 'F', 'G', 'A']
    }
    
    # Score each possible key
    key_scores = {}
    total_notes = sum(pitch_classes.values())
    
    for key, scale_notes in major_patterns.items():
        score = 0
        for note in scale_notes:
            if note in pitch_classes:
                score += pitch_classes[note] / total_notes
        key_scores[key] = score
    
    # Return top 3 key candidates
    sorted_keys = sorted(key_scores.items(), key=lambda x: x[1], reverse=True)
    return [key for key, score in sorted_keys[:3] if score > 0.1]


def categorize_tempo(bpm: float) -> str:
    """
    Categorize tempo into musical terms
    
    Args:
        bpm: Beats per minute
        
    Returns:
        Tempo category string
    """
    if bpm < 60:
        return "Very Slow (Largo)"
    elif bpm < 80:
        return "Slow (Adagio)"
    elif bpm < 100:
        return "Moderate (Andante)"
    elif bpm < 120:
        return "Medium (Moderato)"
    elif bpm < 140:
        return "Fast (Allegro)"
    elif bpm < 180:
        return "Very Fast (Presto)"
    else:
        return "Extremely Fast (Prestissimo)"


def analyze_musical_complexity(features: Dict[str, Any]) -> Dict[str, str]:
    """
    Analyze the musical complexity based on extracted features
    
    Args:
        features: Musical features dictionary
        
    Returns:
        Dictionary describing various aspects of musical complexity
    """
    complexity = {}
    
    # Melodic complexity
    pitch_std = features['pitch_range']['std']
    if pitch_std > 10:
        complexity['melody'] = "High (Wide pitch range, varied melodies)"
    elif pitch_std > 5:
        complexity['melody'] = "Medium (Moderate pitch variation)"
    else:
        complexity['melody'] = "Low (Simple, narrow range melodies)"
    
    # Rhythmic complexity
    note_density = features['rhythm']['note_density']
    if note_density > 5:
        complexity['rhythm'] = "High (Dense, complex rhythms)"
    elif note_density > 2:
        complexity['rhythm'] = "Medium (Moderate rhythmic activity)"
    else:
        complexity['rhythm'] = "Low (Simple, sparse rhythms)"
    
    # Dynamic complexity
    velocity_std = features['dynamics']['velocity_std']
    if velocity_std > 20:
        complexity['dynamics'] = "High (Wide dynamic range)"
    elif velocity_std > 10:
        complexity['dynamics'] = "Medium (Some dynamic variation)"
    else:
        complexity['dynamics'] = "Low (Consistent dynamics)"
    
    return complexity