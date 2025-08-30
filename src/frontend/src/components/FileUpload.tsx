import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, Music, Sparkles } from 'lucide-react';

interface FileUploadProps {
  onFileUpload: (file: File) => void;
  onGetRecommendations: (file: File, songName?: string) => void;
  isAnalyzing: boolean;
  isGettingRecommendations: boolean;
}

const FileUpload: React.FC<FileUploadProps> = ({
  onFileUpload,
  onGetRecommendations,
  isAnalyzing,
  isGettingRecommendations,
}) => {
  const [songName, setSongName] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setSelectedFile(acceptedFiles[0]);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'audio/*': ['.mp3', '.wav', '.flac', '.m4a', '.ogg'],
    },
    multiple: false,
    disabled: isAnalyzing || isGettingRecommendations,
  });

  const handleAnalyze = () => {
    if (selectedFile) {
      onFileUpload(selectedFile);
    }
  };

  const handleGetRecommendations = () => {
    if (selectedFile) {
      onGetRecommendations(selectedFile, songName || undefined);
    }
  };

  const isDisabled = isAnalyzing || isGettingRecommendations;

  return (
    <div className="space-y-6">
      {/* File Upload Area */}
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
          ${isDragActive ? 'border-purple-400 bg-purple-50' : 'border-gray-300 hover:border-purple-400'}
          ${isDisabled ? 'opacity-50 cursor-not-allowed' : ''}
        `}
      >
        <input {...getInputProps()} />
        <Upload className="h-12 w-12 mx-auto mb-4 text-gray-400" />
        {isDragActive ? (
          <p className="text-purple-600 text-lg">Drop your music file here...</p>
        ) : (
          <div>
            <p className="text-gray-600 text-lg mb-2">
              Drop your music file here, or click to browse
            </p>
            <p className="text-gray-400 text-sm">
              Supports MP3, WAV, FLAC, M4A, OGG files
            </p>
          </div>
        )}
      </div>

      {/* Selected File Info */}
      {selectedFile && (
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <Music className="h-5 w-5 text-purple-600" />
            <div className="flex-1">
              <p className="font-medium text-gray-900">{selectedFile.name}</p>
              <p className="text-sm text-gray-500">
                {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Song Name Input */}
      {selectedFile && (
        <div>
          <label htmlFor="songName" className="block text-sm font-medium text-gray-700 mb-2">
            Song Name (Optional)
          </label>
          <input
            type="text"
            id="songName"
            value={songName}
            onChange={(e) => setSongName(e.target.value)}
            placeholder="Enter song name for better recommendations"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            disabled={isDisabled}
          />
        </div>
      )}

      {/* Action Buttons */}
      {selectedFile && (
        <div className="flex gap-4">
          <button
            onClick={handleAnalyze}
            disabled={isDisabled}
            className="flex-1 bg-purple-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
          >
            <Music className="h-5 w-5" />
            Analyze Music
          </button>
          
          <button
            onClick={handleGetRecommendations}
            disabled={isDisabled}
            className="flex-1 bg-gradient-to-r from-purple-600 to-pink-600 text-white py-3 px-6 rounded-lg font-medium hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
          >
            <Sparkles className="h-5 w-5" />
            Get Recommendations
          </button>
        </div>
      )}
    </div>
  );
};

export default FileUpload;
