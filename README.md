# 🎵 Vibify - AI-Powered Music Recommendation System

Vibify analyzes the "musical DNA" of your songs using AI-powered pitch detection and provides intelligent music recommendations based on musical characteristics like tempo, pitch range, rhythm patterns, and harmonic content.

## ✨ Features

- **Advanced Audio Analysis**: Uses Spotify's Basic-Pitch model for precise note detection
- **Musical DNA Extraction**: Analyzes tempo, pitch range, rhythm patterns, dynamics, and harmony
- **AI-Powered Recommendations**: Leverages GPT models to find musically similar songs
- **Batch Processing**: Analyze multiple songs at once
- **Flexible Output**: JSON analysis data + human-readable recommendations
- **No API Required**: Can generate prompts for manual use with any LLM

## 🚀 Quick Start

### Installation

1. **Clone and setup**:
```bash
git clone https://github.com/yourname/vibify.git
cd Vibify
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure API (optional)**:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

3. **Add your music**:
```bash
# Place audio files in data/input/
cp your-song.mp3 data/input/
```

### Basic Usage

```bash
# Analyze a song and get recommendations
python src/main.py --audio data/input/your-song.mp3

# Batch analyze all songs in input directory
python src/main.py

# Generate prompt only (no API call)
python src/main.py --audio song.mp3 --no-api
```

## 📊 What Vibify Analyzes

### Musical Characteristics

- **Pitch & Melody**: Range, average pitch, melodic intervals, key signature hints
- **Rhythm & Tempo**: BPM estimation, note density, rhythm patterns
- **Dynamics**: Velocity patterns, dynamic range, expression variety
- **Harmony**: Pitch class distribution, interval analysis
- **Structure**: Song duration, note count, temporal patterns

### Example Output

```json
{
  "pitch_range": {
    "min": 45.2,
    "max": 84.7,
    "mean": 64.3,
    "std": 8.1
  },
  "rhythm": {
    "total_notes": 847,
    "note_density": 3.2,
    "tempo_estimate": 128
  },
  "harmony": {
    "pitch_classes": {"C": 45, "G": 38, "F": 32},
    "interval_distribution": {2: 45, 4: 38, 5: 28}
  }
}
```

## 🎯 Use Cases

- **Music Discovery**: Find new songs similar to your favorites
- **Playlist Curation**: Build cohesive playlists based on musical characteristics
- **Music Production**: Analyze reference tracks for composition inspiration
- **Music Education**: Study musical patterns and characteristics
- **Research**: Quantitative analysis of musical content

## 🛠️ Advanced Usage

### Programmatic Usage

```python
from src.core.analyzer import MusicAnalyzer
from src.core.recommender import MusicRecommendationEngine

# Initialize components
analyzer = MusicAnalyzer()
recommender = MusicRecommendationEngine(openai_api_key="your-key")

# Analyze audio
features = analyzer.extract_music_features("song.mp3")

# Get recommendations
recommendations = recommender.get_recommendations(features, "Song Name")
print(recommendations)
```

### Batch Processing

```python
from src.utils.file_utils import find_audio_files

# Find all audio files
audio_files = find_audio_files("data/input/")

# Analyze each file
for audio_file in audio_files:
    features = analyzer.extract_music_features(audio_file)
    # Process features...
```

## 🔧 Configuration

### Environment Variables

```bash
# Required for API recommendations
OPENAI_API_KEY=your_openai_api_key_here

# Optional customization
OPENAI_MODEL=gpt-4                # Default: gpt-3.5-turbo
OPENAI_MAX_TOKENS=2000           # Default: 1500
OPENAI_TEMPERATURE=0.7           # Default: 0.7
```

### Supported Audio Formats

- MP3 (.mp3)
- WAV (.wav)
- FLAC (.flac)
- M4A (.m4a)
- AAC (.aac)
- OGG (.ogg)
- WMA (.wma)

## 📁 Project Structure

```
Vibify/
├── src/
│   ├── core/           # Core analysis and recommendation engines
│   ├── utils/          # Helper functions
│   ├── config/         # Configuration management
│   └── main.py         # Main application
├── data/
│   ├── input/          # Place audio files here
│   └── output/         # Generated analysis and recommendations
├── tests/              # Unit tests
├── examples/           # Usage examples
└── requirements.txt    # Dependencies
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=src

# Run specific test
python -m pytest tests/test_analyzer.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run tests (`python -m pytest`)
6. Commit changes (`git commit -m 'Add amazing feature'`)
7. Push to branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Spotify's Basic-Pitch**: For the excellent pitch detection model
- **OpenAI**: For powerful language models
- **The Music Community**: For inspiration and feedback

## 🆘 Troubleshooting

### Common Issues

**"No notes detected"**
- Check if audio file is valid and not corrupted
- Ensure audio contains melodic content (not just percussion/noise)
- Try with different audio files

**API Errors**
- Verify your OpenAI API key is correct
- Check your API quota/billing status
- Use `--no-api` flag to generate prompts manually

**Import Errors**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version (requires 3.8+)

### Getting Help

- Check the [examples/](examples/) directory for usage patterns
- Review test files for expected behavior
- Open an issue on GitHub for bugs or feature requests

---

**Made with ❤️ by the Vibify team**