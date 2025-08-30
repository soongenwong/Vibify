"""
Vibify - Music Recommendation System
Main Application Entry Point

Complete pipeline: Audio Analysis -> Feature Extraction -> LLM Recommendations -> Vector Storage
"""

import argparse
import sys
from pathlib import Path

# Add the project root to the system path to enable module imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.core.analyzer import MusicAnalyzer
from src.core.recommender import MusicRecommendationEngine
from src.utils.file_utils import validate_audio_file, save_analysis_results, save_recommendations
from src.utils.weaviate_utils import WeaviateMusicDB, extract_text_from_analysis
from src.config.settings import Settings


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
  python src/main.py --audio song.mp3 --store-vector  # Store in Weaviate
  python src/main.py --audio song.mp3 --find-similar  # Find similar songs in DB
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
        "--store-vector",
        action="store_true",
        help="Store analysis results as vectors in Weaviate database"
    )
    
    parser.add_argument(
        "--find-similar",
        action="store_true",
        help="Find similar songs in Weaviate database"
    )
    
    parser.add_argument(
        "--weaviate-url",
        type=str,
        default="http://localhost:8080",
        help="Weaviate instance URL (default: http://localhost:8080)"
    )
    
    parser.add_argument(
        "--weaviate-key",
        type=str,
        help="Weaviate API key (for Weaviate Cloud)"
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


def print_text_analysis(features, song_name):
    """Print the text representation that will be vectorized"""
    text = extract_text_from_analysis(features, song_name)
    print("\n📝 Text Analysis for Vectorization:")
    print("   " + "─" * 66)
    print(f"   {text}")
    print("   " + "─" * 66)


def handle_vector_operations(args, features, song_name, audio_path):
    """Handle Weaviate vector storage and similarity search operations"""
    
    # Initialize Weaviate connection
    weaviate_db = WeaviateMusicDB(args.weaviate_url, args.weaviate_key)
    
    if not weaviate_db.client:
        print("\n❌ Could not connect to Weaviate. Vector operations skipped.")
        return
    
    # Store vector if requested
    if args.store_vector:
        print("\n🗄️  Step 4: Storing analysis as vector in Weaviate...")
        
        stored_uuid = weaviate_db.store_analysis(features, song_name, str(audio_path))
        if stored_uuid:
            print(f"   ✅ Analysis stored with UUID: {stored_uuid}")
        else:
            print("   ❌ Failed to store analysis")
    
    # Find similar songs if requested
    if args.find_similar:
        print("\n🔍 Step 5: Finding similar songs in database...")
        
        similar_songs = weaviate_db.find_similar_songs(features, song_name, limit=5)
        
        if similar_songs:
            print(f"\n🎯 Found {len(similar_songs)} similar songs:")
            print("   " + "─" * 66)
            
            for i, song in enumerate(similar_songs, 1):
                distance = song.get('similarity_distance', 0)
                similarity_pct = (1 - distance) * 100 if distance < 1 else 0
                
                print(f"   {i}. {song.get('song_name', 'Unknown')}")
                print(f"      Similarity: {similarity_pct:.1f}%")
                print(f"      Tempo: {song.get('tempo', 0):.0f} BPM")
                print(f"      Notes: {song.get('note_count', 0)}")
                print(f"      Duration: {song.get('duration', 0):.1f}s")
                if args.verbose and song.get('analysis_text'):
                    print(f"      Analysis: {song['analysis_text'][:100]}...")
                print()
            
            print("   " + "─" * 66)
        else:
            print("   📭 No similar songs found in database")
    
    # Close connection
    weaviate_db.close()


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
    
    # Generate song name from file path
    song_name = Path(audio_path).stem.replace("_", " ").replace("-", " ").title()
    
    # Show text analysis that will be vectorized
    if args.store_vector or args.find_similar or args.verbose:
        print_text_analysis(features, song_name)
    
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
    
    recommendations = recommender.get_recommendations(features, song_name)
    
    # Display recommendations
    print("\n" + "🎵" + "="*68 + "🎵")
    print("   MUSIC RECOMMENDATIONS")
    print("🎵" + "="*68 + "🎵")
    print(recommendations)
    print("🎵" + "="*68 + "🎵")
    
    # Save recommendations
    if save_recommendations(recommendations, str(recommendations_path), str(audio_path)):
        print(f"\n✅ Recommendations saved: {recommendations_path}")
    
    # Handle vector operations (Step 4 & 5)
    if args.store_vector or args.find_similar:
        handle_vector_operations(args, features, song_name, audio_path)
    
    # Final summary
    print(f"\n🎉 Analysis complete!")
    print(f"   📁 Output directory: {analysis_path.parent}")
    
    # Show additional tips
    if args.store_vector:
        print(f"\n💡 Next time, use --find-similar to discover similar songs!")
    elif not args.store_vector and not args.find_similar:
        print(f"\n💡 Use --store-vector to save this analysis for future similarity searches")
        print(f"   Use --find-similar to search for similar songs in your database")
    
    if not Settings.validate_api_key() and not args.no_api:
        print(f"\n💡 To enable automatic API recommendations:")
        print(f"   export OPENAI_API_KEY='your-key-here'")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())