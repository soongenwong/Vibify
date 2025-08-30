"""
Music Recommendation Engine

This module handles LLM-powered music recommendations based on extracted
musical features from the analyzer module.
"""

import openai
from typing import Dict, Any, Optional
from ..utils.music_utils import format_pitch_classes, format_intervals


class MusicRecommendationEngine:
    """LLM-powered music recommendation system"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Initialize with OpenAI API key
        
        Args:
            openai_api_key (str): Your OpenAI API key
        """
        self.client = None
        if openai_api_key:
            self.client = openai.OpenAI(api_key=openai_api_key)
    
    def create_similarity_prompt(self, features: Dict[str, Any], song_name: Optional[str] = None) -> str:
        """
        Create a detailed prompt for LLM music similarity analysis
        
        Args:
            features: Musical features from MusicAnalyzer
            song_name: Optional song name for context
            
        Returns:
            Formatted prompt for LLM
        """
        if features.get("error"):
            return f"Could not analyze the song: {features['error']}"
        
        song_desc = f"'{song_name}'" if song_name else "this song"
        
        prompt = f"""Analyze {song_desc} based on these musical characteristics:

PITCH & MELODY:
- Pitch range: {features['pitch_range']['min']:.1f} to {features['pitch_range']['max']:.1f} (MIDI notes)
- Average pitch: {features['pitch_range']['mean']:.1f}
- Pitch variety: {features['pitch_range']['std']:.1f}
- Key signature hints: Most used notes are {format_pitch_classes(features['harmony']['pitch_classes'])}

RHYTHM & TEMPO:
- Estimated tempo: {features['temporal']['tempo_estimate']:.0f} BPM
- Note density: {features['rhythm']['note_density']:.1f} notes per second
- Average note duration: {features['rhythm']['avg_duration']:.2f} seconds
- Common rhythm patterns: {features['temporal']['onset_pattern'][:3]}

DYNAMICS & EXPRESSION:
- Average velocity/intensity: {features['dynamics']['avg_velocity']:.0f}/127
- Dynamic range: {features['dynamics']['velocity_range']:.0f} points
- Expression variety: {features['dynamics']['velocity_std']:.1f}

MUSICAL STRUCTURE:
- Total notes detected: {features['rhythm']['total_notes']}
- Song duration: {features['temporal']['song_duration']:.1f} seconds
- Common melodic intervals: {format_intervals(features['harmony']['interval_distribution'])}

Based on these musical DNA characteristics, recommend 5 similar songs that share:
1. Similar tempo and rhythm patterns
2. Comparable pitch range and melodic movement
3. Similar musical complexity and note density
4. Matching dynamic expression style

For each recommendation, provide:
- Song title and artist
- Specific musical similarities (tempo, key, rhythm, etc.)
- Why it matches the analyzed characteristics"""

        return prompt
    
    def get_recommendations(self, features: Dict[str, Any], song_name: Optional[str] = None) -> str:
        """
        Get song recommendations from GPT API
        
        Args:
            features: Musical features from MusicAnalyzer
            song_name: Optional song name for context
            
        Returns:
            GPT recommendations or error message with manual prompt
        """
        if not self.client:
            prompt = self.create_similarity_prompt(features, song_name)
            return f"No API key provided. Here's the prompt to use manually:\n\n{prompt}"
        
        prompt = self.create_similarity_prompt(features, song_name)
        
        try:
            print("Calling OpenAI API for recommendations...")
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a music expert who analyzes musical characteristics to recommend similar songs. Provide specific, accurate song recommendations with detailed explanations of musical similarities."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower():
                return f"API quota exceeded. Here's the prompt to use manually:\n\n{prompt}"
            elif "api_key" in error_msg.lower():
                return f"Invalid API key. Here's the prompt to use manually:\n\n{prompt}"
            else:
                return f"API error: {error_msg}\n\nHere's the prompt to use manually:\n\n{prompt}"