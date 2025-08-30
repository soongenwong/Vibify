import os
import json
import pandas as pd
import numpy as np
from pathlib import Path
from basic_pitch.inference import predict
import openai

class MusicAnalyzer:
    def __init__(self):
        """Initialize the music analyzer with Basic-Pitch model"""
        pass
        
    def extract_music_features(self, audio_path):
        """
        Extract comprehensive music features from audio file
        
        Args:
            audio_path (str): Path to audio file (.mp3, .wav, .flac, etc.)
            
        Returns:
            dict: Musical features for LLM analysis
        """
        print(f"Analyzing {audio_path}...")
        
        try:
            # Run Basic-Pitch inference
            model_output, midi_data, note_events = predict(audio_path)
            
            # Convert note_events to proper format if needed
            if note_events and len(note_events) > 0:
                # Check if note_events is in tuple format and convert to dict
                formatted_events = []
                for event in note_events:
                    if isinstance(event, tuple):
                        # Format: (start_time, end_time, pitch, velocity, confidence_data)
                        formatted_events.append({
                            'start_time': event[0],
                            'end_time': event[1],
                            'duration': event[1] - event[0],
                            'pitch': event[2],
                            'velocity': event[3],
                            'confidence': event[4] if len(event) > 4 else 0.5
                        })
                    else:
                        formatted_events.append(event)
                
                # Extract meaningful features from note events
                features = self._analyze_note_events(formatted_events)
                return features
            else:
                return {"error": "No notes detected"}
            
        except Exception as e:
            print(f"Error analyzing {audio_path}: {e}")
            return None
    
    def _analyze_note_events(self, note_events):
        """
        Analyze note events to extract musical characteristics
        
        Args:
            note_events (list): List of note events from Basic-Pitch
            
        Returns:
            dict: Analyzed musical features
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
    
    def _analyze_onset_pattern(self, df):
        """Analyze rhythm patterns from note onsets"""
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
    
    def _estimate_tempo(self, df):
        """Rough tempo estimation from note density"""
        if df['end_time'].max() == 0:
            return 0
        
        # Calculate notes per second, convert to approximate BPM
        notes_per_second = len(df) / df['end_time'].max()
        # Rough estimation: assume 4 notes per beat on average
        estimated_bpm = notes_per_second * 15  # 60 / 4 = 15
        
        return float(estimated_bpm)
    
    def _get_pitch_classes(self, df):
        """Get pitch class distribution (C, C#, D, etc.)"""
        pitch_classes = df['pitch'] % 12
        unique, counts = np.unique(pitch_classes, return_counts=True)
        
        # Convert to note names
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        pitch_class_dist = {}
        
        for pc, count in zip(unique, counts):
            pitch_class_dist[note_names[int(pc)]] = int(count)
            
        return pitch_class_dist
    
    def _analyze_intervals(self, df):
        """Analyze melodic intervals"""
        pitches = sorted(df['pitch'].values)
        if len(pitches) < 2:
            return {}
        
        intervals = np.diff(pitches)
        # Focus on intervals within an octave
        intervals = intervals[abs(intervals) <= 12]
        
        unique, counts = np.unique(intervals, return_counts=True)
        
        # Return most common intervals
        return dict(zip(unique.astype(int).tolist(), counts.astype(int).tolist()))

class MusicRecommendationEngine:
    def __init__(self, openai_api_key=None):
        """
        Initialize with OpenAI API key
        
        Args:
            openai_api_key (str): Your OpenAI API key
        """
        self.client = None
        if openai_api_key:
            self.client = openai.OpenAI(api_key=openai_api_key)
    
    def create_similarity_prompt(self, features, song_name=None):
        """
        Create a detailed prompt for LLM music similarity analysis
        
        Args:
            features (dict): Musical features from MusicAnalyzer
            song_name (str): Optional song name
            
        Returns:
            str: Formatted prompt for LLM
        """
        if features.get("error"):
            return f"Could not analyze the song: {features['error']}"
        
        song_desc = f"'{song_name}'" if song_name else "this song"
        
        prompt = f"""Analyze {song_desc} based on these musical characteristics:

PITCH & MELODY:
- Pitch range: {features['pitch_range']['min']:.1f} to {features['pitch_range']['max']:.1f} (MIDI notes)
- Average pitch: {features['pitch_range']['mean']:.1f}
- Pitch variety: {features['pitch_range']['std']:.1f}
- Key signature hints: Most used notes are {self._format_pitch_classes(features['harmony']['pitch_classes'])}

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
- Common melodic intervals: {self._format_intervals(features['harmony']['interval_distribution'])}

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
    
    def get_recommendations(self, features, song_name=None):
        """
        Get song recommendations from GPT API
        
        Args:
            features (dict): Musical features from MusicAnalyzer
            song_name (str): Optional song name
            
        Returns:
            str: GPT recommendations or error message
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
                    {"role": "system", "content": "You are a music expert who analyzes musical characteristics to recommend similar songs. Provide specific, accurate song recommendations with detailed explanations of musical similarities."},
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
    
    def _format_pitch_classes(self, pitch_classes):
        """Format pitch class distribution for readability"""
        sorted_pc = sorted(pitch_classes.items(), key=lambda x: x[1], reverse=True)
        return ", ".join([f"{note}({count})" for note, count in sorted_pc[:4]])
    
    def _format_intervals(self, intervals):
        """Format interval distribution for readability"""
        if not intervals:
            return "No clear patterns"
        
        sorted_intervals = sorted(intervals.items(), key=lambda x: x[1], reverse=True)
        return ", ".join([f"{interval}({count})" for interval, count in sorted_intervals[:3]])

def main():
    """Complete pipeline: Audio -> Analysis -> GPT Recommendations"""
    
    # Configuration
    AUDIO_FILE = "hate-to-love.mp3"  # Change this to your audio file
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    print("🎵 Music Recommendation System Starting...")
    print(f"Audio file: {AUDIO_FILE}")
    print(f"API key configured: {'Yes' if OPENAI_API_KEY else 'No'}")
    
    # Check if audio file exists
    if not os.path.exists(AUDIO_FILE):
        print(f"Error: {AUDIO_FILE} not found!")
        print("Place your music file in the same directory as this script.")
        return
    
    # Initialize components
    analyzer = MusicAnalyzer()
    recommender = MusicRecommendationEngine(openai_api_key=OPENAI_API_KEY)
    
    # Step 1: Extract musical features
    print("\n🔍 Step 1: Analyzing musical characteristics...")
    features = analyzer.extract_music_features(AUDIO_FILE)
    
    if features is None:
        print("Failed to extract features from audio file.")
        return
    
    if features.get("error"):
        print(f"Analysis error: {features['error']}")
        return
    
    # Step 2: Save analysis results
    print("💾 Step 2: Saving analysis results...")
    
    # Save detailed features
    with open("music_analysis.json", 'w') as f:
        json_features = json.loads(json.dumps(features, default=str))
        json.dump(json_features, f, indent=2)
    
    # Print summary
    print(f"   → Found {features['rhythm']['total_notes']} notes")
    print(f"   → Estimated tempo: {features['temporal']['tempo_estimate']:.0f} BPM")
    print(f"   → Pitch range: {features['pitch_range']['min']:.0f}-{features['pitch_range']['max']:.0f}")
    print(f"   → Song duration: {features['temporal']['song_duration']:.1f}s")
    
    # Step 3: Get recommendations
    print("\n🤖 Step 3: Getting song recommendations...")
    
    recommendations = recommender.get_recommendations(features, AUDIO_FILE)
    
    # Step 4: Display and save results
    print("\n" + "="*70)
    print("🎵 MUSIC RECOMMENDATIONS")
    print("="*70)
    print(recommendations)
    print("="*70)
    
    # Save recommendations
    with open("song_recommendations.txt", "w") as f:
        f.write(f"Music Recommendations for {AUDIO_FILE}\n")
        f.write("="*50 + "\n\n")
        f.write(recommendations)
    
    print(f"\n✅ Complete! Results saved to:")
    print(f"   • music_analysis.json - Detailed musical features")
    print(f"   • song_recommendations.txt - GPT recommendations")
    
    # Optional: Show prompt for manual use
    if not OPENAI_API_KEY:
        print(f"\n💡 To use API automatically:")
        print(f"   export OPENAI_API_KEY='your-key-here'")
        print(f"   pip install openai")

if __name__ == "__main__":
    main()