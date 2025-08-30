import React from 'react';
import { BarChart, Clock, Music, Volume2, Waves } from 'lucide-react';
import type { AnalysisResult } from '../types/api';

interface AnalysisResultsProps {
  result: AnalysisResult;
}

const AnalysisResults: React.FC<AnalysisResultsProps> = ({ result }) => {
  const { features } = result;

  const formatNote = (midiNote: number): string => {
    const noteNames = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
    const octave = Math.floor(midiNote / 12) - 1;
    const note = noteNames[Math.floor(midiNote) % 12];
    return `${note}${octave}`;
  };

  const formatDuration = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const getMostUsedNotes = () => {
    return Object.entries(features.harmony.pitch_classes)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 5)
      .map(([note, count]) => ({ note, count }));
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center gap-3 mb-6">
        <BarChart className="h-6 w-6 text-purple-600" />
        <h2 className="text-2xl font-bold text-gray-900">Music Analysis Results</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Tempo & Rhythm */}
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Clock className="h-5 w-5 text-purple-600" />
            <h3 className="font-semibold text-gray-900">Tempo & Rhythm</h3>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-600">Estimated BPM:</span>
              <span className="font-medium">{Math.round(features.temporal.tempo_estimate)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Note Density:</span>
              <span className="font-medium">{features.rhythm.note_density.toFixed(1)} notes/sec</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Duration:</span>
              <span className="font-medium">{formatDuration(features.temporal.song_duration)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Total Notes:</span>
              <span className="font-medium">{features.rhythm.total_notes}</span>
            </div>
          </div>
        </div>

        {/* Pitch Range */}
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Music className="h-5 w-5 text-purple-600" />
            <h3 className="font-semibold text-gray-900">Pitch Range</h3>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-600">Lowest Note:</span>
              <span className="font-medium">{formatNote(features.pitch_range.min)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Highest Note:</span>
              <span className="font-medium">{formatNote(features.pitch_range.max)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Average Pitch:</span>
              <span className="font-medium">{formatNote(features.pitch_range.mean)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Range:</span>
              <span className="font-medium">
                {(features.pitch_range.max - features.pitch_range.min).toFixed(0)} semitones
              </span>
            </div>
          </div>
        </div>

        {/* Dynamics */}
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Volume2 className="h-5 w-5 text-purple-600" />
            <h3 className="font-semibold text-gray-900">Dynamics</h3>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-600">Avg Velocity:</span>
              <span className="font-medium">{Math.round(features.dynamics.avg_velocity * 127)}/127</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Dynamic Range:</span>
              <span className="font-medium">{Math.round(features.dynamics.velocity_range * 127)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Expression:</span>
              <span className="font-medium">
                {features.dynamics.velocity_std > 0.15 ? 'High' : 
                 features.dynamics.velocity_std > 0.08 ? 'Medium' : 'Low'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Musical Key Analysis */}
      <div className="mt-6 bg-gray-50 rounded-lg p-4">
        <div className="flex items-center gap-2 mb-3">
          <Waves className="h-5 w-5 text-purple-600" />
          <h3 className="font-semibold text-gray-900">Musical Characteristics</h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <h4 className="font-medium text-gray-700 mb-2">Most Used Notes:</h4>
            <div className="flex flex-wrap gap-2">
              {getMostUsedNotes().map(({ note, count }) => (
                <span
                  key={note}
                  className="bg-purple-100 text-purple-800 px-2 py-1 rounded text-sm font-medium"
                >
                  {note} ({count})
                </span>
              ))}
            </div>
          </div>
          
          <div>
            <h4 className="font-medium text-gray-700 mb-2">Rhythm Patterns:</h4>
            <div className="text-sm text-gray-600">
              Common intervals: {features.temporal.onset_pattern.slice(0, 3).map(p => `${p}s`).join(', ')}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalysisResults;
