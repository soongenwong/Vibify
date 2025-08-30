import React from 'react';
import { Sparkles, ExternalLink, Music } from 'lucide-react';
import type { RecommendationResult } from '../types/api';

interface RecommendationsProps {
  result: RecommendationResult;
}

const Recommendations: React.FC<RecommendationsProps> = ({ result }) => {
  const formatRecommendations = (text: string) => {
    // Split by common patterns to identify song recommendations
    const lines = text.split('\n').filter(line => line.trim());
    const formattedLines = lines.map((line, index) => {
      // Check if line contains song title and artist pattern
      if (line.match(/^\d+\.|•|-/) || line.includes(' by ') || line.includes(' - ')) {
        return (
          <div key={index} className="bg-purple-50 border-l-4 border-purple-500 p-3 my-2">
            <p className="font-medium text-purple-900">{line}</p>
          </div>
        );
      }
      
      // Regular text
      return (
        <p key={index} className="text-gray-700 mb-2">
          {line}
        </p>
      );
    });
    
    return formattedLines;
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center gap-3 mb-6">
        <Sparkles className="h-6 w-6 text-purple-600" />
        <h2 className="text-2xl font-bold text-gray-900">AI Song Recommendations</h2>
      </div>

      {/* Song Info */}
      <div className="bg-gradient-to-r from-purple-100 to-pink-100 rounded-lg p-4 mb-6">
        <div className="flex items-center gap-3">
          <Music className="h-6 w-6 text-purple-600" />
          <div>
            <h3 className="font-semibold text-gray-900">Analyzed Track</h3>
            <p className="text-gray-600">{result.song_name}</p>
          </div>
        </div>
      </div>

      {/* Musical Characteristics Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-gray-50 rounded-lg p-3 text-center">
          <div className="text-lg font-bold text-purple-600">
            {Math.round(result.features.temporal.tempo_estimate)}
          </div>
          <div className="text-sm text-gray-600">BPM</div>
        </div>
        <div className="bg-gray-50 rounded-lg p-3 text-center">
          <div className="text-lg font-bold text-purple-600">
            {result.features.rhythm.total_notes}
          </div>
          <div className="text-sm text-gray-600">Notes</div>
        </div>
        <div className="bg-gray-50 rounded-lg p-3 text-center">
          <div className="text-lg font-bold text-purple-600">
            {Math.round(result.features.temporal.song_duration)}s
          </div>
          <div className="text-sm text-gray-600">Duration</div>
        </div>
        <div className="bg-gray-50 rounded-lg p-3 text-center">
          <div className="text-lg font-bold text-purple-600">
            {result.features.rhythm.note_density.toFixed(1)}
          </div>
          <div className="text-sm text-gray-600">Notes/sec</div>
        </div>
      </div>

      {/* Recommendations */}
      <div className="prose max-w-none">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Based on your track's musical DNA, here are our recommendations:
        </h3>
        
        <div className="bg-gray-50 rounded-lg p-4">
          {formatRecommendations(result.recommendations)}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="mt-6 flex flex-wrap gap-3">
        <button
          onClick={() => navigator.clipboard.writeText(result.recommendations)}
          className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors"
        >
          Copy Recommendations
        </button>
        
        <button
          onClick={() => {
            const blob = new Blob([result.recommendations], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `recommendations-${result.song_name}.txt`;
            a.click();
            URL.revokeObjectURL(url);
          }}
          className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors flex items-center gap-2"
        >
          <ExternalLink className="h-4 w-4" />
          Export as Text
        </button>
      </div>

      {/* Note about API */}
      {result.recommendations.includes('No API key') && (
        <div className="mt-4 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <h4 className="font-medium text-yellow-800">API Key Not Configured</h4>
          <p className="text-yellow-700 mt-1 text-sm">
            To get AI-powered recommendations automatically, configure your OpenAI API key in the backend.
            The generated prompt above can be used manually with ChatGPT or other AI services.
          </p>
        </div>
      )}
    </div>
  );
};

export default Recommendations;
