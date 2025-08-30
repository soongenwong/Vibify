"""
Sample Usage Examples for Vibify

This file demonstrates various ways to use the Vibify music recommendation system.
"""

import sys
import os
from pathlib import Path

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from core.analyzer import MusicAnalyzer
from core.recommender import MusicRecommendationEngine
from utils.file_utils import validate_audio_file, find_audio_files
from config.settings import Settings


def basic_usage_example():
    """Basic usage: analyze one song and get recommendations"""
    print("=== Basic Usage Example ===")
    
    # Set up paths
    audio_file = "data/input/sample_song.mp3"
    
    if not validate_audio_file(audio_file):
        print(f"Please place an audio file at: {audio_file}")
        return
    
    # Initialize components
    analyzer = MusicAnalyzer()
    recommender = MusicRecommendationEngine(openai_api_key=os.getenv("OPENAI_API_KEY"))
    
    # Analyze music
    features = analyzer.extract_music_features(audio_file)
    
    if features and not features.get("error"):
        print(f"✅ Successfully analyzed {audio_file}")
        
        # Get recommendations
        recommendations = recommender.get_recommendations(features, "Sample Song")
        print("\n🎵 Recommendations:")
        print(recommendations)
    else:
        print(f"❌ Failed to analyze {audio_file}")


def batch_analysis_example():
    """Batch analysis: analyze multiple songs in a directory"""
    print("\n=== Batch Analysis Example ===")
    
    input_dir = "data/input"
    audio_files = find_audio_files(input_dir)
    
    if not audio_files:
        print(f"No audio files found in {input_dir}")
        return
    
    print(f"Found {len(audio_files)} audio files:")
    
    analyzer = MusicAnalyzer()
    recommender = MusicRecommendationEngine(openai_api_key=os.getenv("OPENAI_API_KEY"))
    
    for audio_file in audio_files:
        print(f"\n🎧 Analyzing: {Path(audio_file).name}")
        
        features = analyzer.extract_music_features(audio_file)
        
        if features and not features.get("error"):
            # Save individual analysis
            output_path = Settings.get_analysis_output_path(Path(audio_file).name)
            
            with open(output_path, 'w') as f:
                import json
                json.dump(features, f, indent=2, default=str)
            
            print(f"   ✅ Analysis saved: {output_path}")
            
            # Quick feature summary
            print(f"   📊 {features['rhythm']['total_notes']} notes, "
                  f"{features['temporal']['tempo_estimate']:.0f} BPM")
        else:
            print(f"   ❌ Failed to analyze")


def custom_analysis_example():
    """Custom analysis: access individual feature components"""
    print("\n=== Custom Analysis Example ===")
    
    audio_file = "data/input/sample_song.mp3"
    
    if not validate_audio_file(audio_file):
        print(f"Please place an audio file at: {audio_file}")
        return
    
    analyzer = MusicAnalyzer()
    features = analyzer.extract_music_features(audio_file)
    
    if features and not features.get("error"):
        print("🎼 Detailed Musical Analysis:")
        
        # Pitch analysis
        pitch_info = features['pitch_range']
        print(f"\n🎹 Pitch Characteristics:")
        print(f"   Range: {pitch_info['min']:.1f} - {pitch_info['max']:.1f} MIDI")
        print(f"   Average: {pitch_info['mean']:.1f}")
        print(f"   Variation: {pitch_info['std']:.1f}")
        
        # Rhythm analysis
        rhythm_info = features['rhythm']
        print(f"\n🥁 Rhythm Characteristics:")
        print(f"   Total notes: {rhythm_info['total_notes']}")
        print(f"   Note density: {rhythm_info['note_density']:.2f} notes/sec")
        print(f"   Avg duration: {rhythm_info['avg_duration']:.3f}s")
        
        # Harmony analysis
        harmony_info = features['harmony']
        print(f"\n🎵 Harmony Hints:")
        print(f"   Pitch classes: {harmony_info['pitch_classes']}")
        print(f"   Common intervals: {harmony_info['interval_distribution']}")
        
        # Tempo analysis
        tempo = features['temporal']['tempo_estimate']
        print(f"\n⏱️  Tempo: {tempo:.0f} BPM")
        
        from utils.music_utils import categorize_tempo
        tempo_category = categorize_tempo(tempo)
        print(f"   Category: {tempo_category}")


def prompt_only_example():
    """Example of generating prompts without API calls"""
    print("\n=== Prompt-Only Example ===")
    
    audio_file = "data/input/sample_song.mp3"
    
    if not validate_audio_file(audio_file):
        print(f"Please place an audio file at: {audio_file}")
        return
    
    # Analyze without API
    analyzer = MusicAnalyzer()
    recommender = MusicRecommendationEngine()  # No API key
    
    features = analyzer.extract_music_features(audio_file)
    
    if features and not features.get("error"):
        prompt = recommender.create_similarity_prompt(features, "Sample Song")
        
        print("📝 Generated Prompt for Manual Use:")
        print("-" * 50)
        print(prompt)
        print("-" * 50)
        print("\n💡 Copy this prompt and use it with ChatGPT, Claude, or any LLM!")


def main():
    """Run all examples"""
    print("🎵 Vibify Usage Examples\n")
    
    # Ensure directories exist
    Settings.ensure_directories()
    
    # Run examples
    basic_usage_example()
    batch_analysis_example()
    custom_analysis_example()
    prompt_only_example()
    
    print("\n🎉 Examples complete!")
    print("💡 Edit the audio file paths in this script to test with your own music.")


if __name__ == "__main__":
    main()