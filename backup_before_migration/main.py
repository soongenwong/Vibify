"""
Vibify - Music Recommendation System
Main Application Entry Point

Complete pipeline: Audio Analysis -> Feature Extraction -> LLM Recommendations
"""

import argparse
import sys
from pathlib import Path

from core.analyzer import MusicAnalyzer
from core.recommender import MusicRecommendationEngine
from utils.file_utils import validate_audio_file, save_analysis_results, save_recommendations
from config.settings import Settings


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Vibify - AI-Powered Music Recommendation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/main.py --audio data/input/song.mp3
  python src/main.py --audio song.wav --output-dir custom_output/
  python src/main.py --audio song.mp3 --no-api  # Generate prompt only
        """
    )
    
    parser.add_argument(
        "--audio", "-a",
        type=str,
        help="Path to audio file for analysis"
    )
    
    parser.add_argument(
        "--output-dir", "-o",
        type=str,
        default=None,
        help="Custom output directory (default: data/output/)"
    )
    
    parser.add_argument(
        "--no-api",
        action="store_true",
        help="Skip API call and generate prompt only"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    return parser.parse_args()


def print_banner():
    """Print application banner"""
    print("🎵" + "="*68 + "🎵")
    print("   VIBIFY - AI-Powered Music Recommendation System")
    print("   Analyze musical DNA and discover similar songs")
    print("🎵" + "="*68 + "🎵")


def print_feature_summary(features):
    """Print a summary of extracted features"""
    if features.get("error"):
        print(f"❌ Analysis failed: {features['error']}")
        return
    
    print("\n📊 Musical Analysis Summary:")
    print(f"   • Notes detected: {features['rhythm']['total_notes']}")
    print(f"   • Song duration: {features['temporal']['song_duration']:.1f}s")
    print(f"   • Estimated tempo: {features['temporal']['tempo_estimate']:.0f} BPM")
    print(f"   • Pitch range: {features['pitch_range']['min']:.0f}-{features['pitch_range']['max']:.0f} (MIDI)")
    print(f"   • Note density: {features['rhythm']['note_density']:.1f} notes/second")
    print(f"   • Average velocity: {features['dynamics']['avg_velocity']:.0f}/127")


def main():
    """Main application pipeline"""
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Print banner
    print_banner()
    
    # Ensure project directories exist
    Settings.ensure_directories()
    
    # Determine audio file path
    if args.audio:
        audio_path = args.audio
    else:
        # Try to find audio file in input directory
        audio_path = Settings.get_input_path(Settings.DEFAULT_AUDIO_FILE)
        
        if not audio_path.exists():
            print(f"\n❌ No audio file specified and default file not found.")
            print(f"Expected: {audio_path}")
            print(f"\nUsage: python src/main.py --audio path/to/your/song.mp3")
            print(f"Or place '{Settings.DEFAULT_AUDIO_FILE}' in data/input/")
            return 1
    
    # Validate audio file
    if not validate_audio_file(audio_path):
        return 1
    
    print(f"\n🎧 Analyzing: {Path(audio_path).name}")
    
    # Initialize components
    analyzer = MusicAnalyzer()
    
    # Don't initialize recommender with API key if --no-api flag is set
    api_key = None if args.no_api else Settings.OPENAI_API_KEY
    recommender = MusicRecommendationEngine(openai_api_key=api_key)
    
    # Step 1: Extract musical features
    print("\n🔍 Step 1: Extracting musical features...")
    features = analyzer.extract_music_features(str(audio_path))
    
    if features is None:
        print("❌ Failed to extract features from audio file.")
        return 1
    
    # Print feature summary
    print_feature_summary(features)
    
    # Step 2: Save analysis results
    print("\n💾 Step 2: Saving analysis results...")
    
    # Determine output paths
    if args.output_dir:
        output_dir = Path(args.output_dir)
        analysis_path = output_dir / f"{Path(audio_path).stem}_analysis.json"
        recommendations_path = output_dir / f"{Path(audio_path).stem}_recommendations.txt"
    else:
        analysis_path = Settings.get_analysis_output_path(Path(audio_path).name)
        recommendations_path = Settings.get_recommendations_output_path(Path(audio_path).name)
    
    # Save features
    if save_analysis_results(features, str(analysis_path)):
        print(f"   ✅ Analysis saved: {analysis_path}")
    
    # Step 3: Get recommendations
    print("\n🤖 Step 3: Generating recommendations...")
    
    if args.no_api:
        print("   ℹ️  API disabled - generating prompt only")
    elif not Settings.validate_api_key():
        print("   ⚠️  No OpenAI API key found - generating prompt only")
        print("   💡 Set OPENAI_API_KEY environment variable to enable API calls")
    
    song_name = Path(audio_path).stem.replace("_", " ").replace("-", " ").title()
    recommendations = recommender.get_recommendations(features, song_name)
    
    # Step 4: Display and save results
    print("\n" + "🎵" + "="*68 + "🎵")
    print("   MUSIC RECOMMENDATIONS")
    print("🎵" + "="*68 + "🎵")
    print(recommendations)
    print("🎵" + "="*68 + "🎵")
    
    # Save recommendations
    if save_recommendations(recommendations, str(recommendations_path), str(audio_path)):
        print(f"\n✅ Recommendations saved: {recommendations_path}")
    
    # Final summary
    print(f"\n🎉 Analysis complete!")
    print(f"   📁 Output directory: {analysis_path.parent}")
    
    if not Settings.validate_api_key() and not args.no_api:
        print(f"\n💡 To enable automatic API recommendations:")
        print(f"   export OPENAI_API_KEY='your-key-here'")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())