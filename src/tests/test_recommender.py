# tests/test_recommender.py
"""
Unit tests for MusicRecommendationEngine
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from core.recommender import MusicRecommendationEngine


class TestMusicRecommendationEngine:
    
    def setup_method(self):
        """Set up test fixtures"""
        self.sample_features = {
            'pitch_range': {'min': 60.0, 'max': 72.0, 'mean': 66.0, 'std': 3.5},
            'rhythm': {'total_notes': 100, 'note_density': 2.5, 'avg_duration': 0.4, 'duration_std': 0.2},
            'dynamics': {'avg_velocity': 80.0, 'velocity_range': 40.0, 'velocity_std': 15.0},
            'temporal': {'song_duration': 40.0, 'onset_pattern': [0.25, 0.5, 1.0], 'tempo_estimate': 120.0},
            'harmony': {'pitch_classes': {'C': 20, 'G': 15, 'F': 10}, 'interval_distribution': {2: 10, 4: 8, 5: 6}}
        }
    
    def test_create_similarity_prompt(self):
        """Test prompt creation"""
        recommender = MusicRecommendationEngine()
        
        prompt = recommender.create_similarity_prompt(self.sample_features, "Test Song")
        
        assert "Test Song" in prompt
        assert "120 BPM" in prompt
        assert "60.0 to 72.0" in prompt
        assert "PITCH & MELODY" in prompt
        assert "recommend 5 similar songs" in prompt
    
    def test_create_similarity_prompt_no_song_name(self):
        """Test prompt creation without song name"""
        recommender = MusicRecommendationEngine()
        
        prompt = recommender.create_similarity_prompt(self.sample_features)
        
        assert "this song" in prompt
        assert "120 BPM" in prompt
    
    def test_create_similarity_prompt_error(self):
        """Test prompt creation with error features"""
        recommender = MusicRecommendationEngine()
        error_features = {"error": "No notes detected"}
        
        prompt = recommender.create_similarity_prompt(error_features)
        
        assert "Could not analyze the song" in prompt
        assert "No notes detected" in prompt
    
    def test_get_recommendations_no_api_key(self):
        """Test recommendations without API key"""
        recommender = MusicRecommendationEngine()  # No API key
        
        result = recommender.get_recommendations(self.sample_features)
        
        assert "No API key provided" in result
        assert "Here's the prompt to use manually" in result
    
    @patch('openai.OpenAI')
    def test_get_recommendations_success(self, mock_openai):
        """Test successful API recommendations"""
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Mock recommendations"
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        recommender = MusicRecommendationEngine(openai_api_key="test_key")
        result = recommender.get_recommendations(self.sample_features)
        
        assert result == "Mock recommendations"
        
        # Verify API call parameters
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]['model'] == 'gpt-3.5-turbo'
        assert call_args[1]['max_tokens'] == 1500
        assert call_args[1]['temperature'] == 0.7
    
    @patch('openai.OpenAI')
    def test_get_recommendations_api_error(self, mock_openai):
        """Test API error handling"""
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client
        
        recommender = MusicRecommendationEngine(openai_api_key="test_key")
        result = recommender.get_recommendations(self.sample_features)
        
        assert "API error" in result
        assert "Here's the prompt to use manually" in result
    
    @patch('openai.OpenAI')
    def test_get_recommendations_quota_exceeded(self, mock_openai):
        """Test quota exceeded error handling"""
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("quota exceeded")
        mock_openai.return_value = mock_client
        
        recommender = MusicRecommendationEngine(openai_api_key="test_key")
        result = recommender.get_recommendations(self.sample_features)
        
        assert "API quota exceeded" in result
        assert "Here's the prompt to use manually" in result
    
    @patch('openai.OpenAI')
    def test_get_recommendations_invalid_api_key(self, mock_openai):
        """Test invalid API key error handling"""
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("invalid api_key")
        mock_openai.return_value = mock_client
        
        recommender = MusicRecommendationEngine(openai_api_key="invalid_key")
        result = recommender.get_recommendations(self.sample_features)
        
        assert "Invalid API key" in result
        assert "Here's the prompt to use manually" in result