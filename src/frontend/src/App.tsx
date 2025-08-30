import { useState } from 'react'
import { Upload, Music, Brain, Loader2 } from 'lucide-react'
import FileUpload from './components/FileUpload'
import AnalysisResults from './components/AnalysisResults'
import Recommendations from './components/Recommendations'
import { analyzeMusic, getRecommendations } from './services/api'
import type { AnalysisResult, RecommendationResult } from './types/api'

function App() {
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [isGettingRecommendations, setIsGettingRecommendations] = useState(false)
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null)
  const [recommendations, setRecommendations] = useState<RecommendationResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleFileUpload = async (file: File) => {
    setIsAnalyzing(true)
    setError(null)
    setAnalysisResult(null)
    setRecommendations(null)

    try {
      const result = await analyzeMusic(file)
      setAnalysisResult(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze music')
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleGetRecommendations = async (file: File, songName?: string) => {
    setIsGettingRecommendations(true)
    setError(null)

    try {
      const result = await getRecommendations(file, songName)
      setRecommendations(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get recommendations')
    } finally {
      setIsGettingRecommendations(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Music className="h-12 w-12 text-purple-600" />
            <h1 className="text-4xl font-bold text-gray-900">Vibify</h1>
          </div>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Discover the musical DNA of your favorite tracks and get AI-powered song recommendations
          </p>
        </div>

        {/* Error Display */}
        {error && (
          <div className="max-w-2xl mx-auto mb-8">
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <h3 className="text-red-800 font-medium">Error</h3>
              <p className="text-red-700 mt-1">{error}</p>
            </div>
          </div>
        )}

        {/* File Upload */}
        <div className="max-w-2xl mx-auto mb-8">
          <FileUpload
            onFileUpload={handleFileUpload}
            onGetRecommendations={handleGetRecommendations}
            isAnalyzing={isAnalyzing}
            isGettingRecommendations={isGettingRecommendations}
          />
        </div>

        {/* Loading States */}
        {(isAnalyzing || isGettingRecommendations) && (
          <div className="max-w-2xl mx-auto mb-8">
            <div className="bg-white rounded-lg shadow-lg p-8">
              <div className="flex items-center justify-center gap-3">
                <Loader2 className="h-6 w-6 animate-spin text-purple-600" />
                <span className="text-lg font-medium text-gray-700">
                  {isAnalyzing && 'Analyzing musical features...'}
                  {isGettingRecommendations && 'Getting AI recommendations...'}
                </span>
              </div>
              <p className="text-center text-gray-500 mt-2">
                This may take a few moments
              </p>
            </div>
          </div>
        )}

        {/* Analysis Results */}
        {analysisResult && !isAnalyzing && (
          <div className="max-w-4xl mx-auto mb-8">
            <AnalysisResults result={analysisResult} />
          </div>
        )}

        {/* Recommendations */}
        {recommendations && !isGettingRecommendations && (
          <div className="max-w-4xl mx-auto">
            <Recommendations result={recommendations} />
          </div>
        )}

        {/* Features Section */}
        {!analysisResult && !recommendations && !isAnalyzing && !isGettingRecommendations && (
          <div className="max-w-4xl mx-auto">
            <div className="grid md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="bg-white rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4 shadow-lg">
                  <Upload className="h-8 w-8 text-purple-600" />
                </div>
                <h3 className="font-semibold text-lg mb-2">Upload Your Music</h3>
                <p className="text-gray-600">
                  Support for MP3, WAV, FLAC, and other popular audio formats
                </p>
              </div>
              
              <div className="text-center">
                <div className="bg-white rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4 shadow-lg">
                  <Brain className="h-8 w-8 text-purple-600" />
                </div>
                <h3 className="font-semibold text-lg mb-2">AI Analysis</h3>
                <p className="text-gray-600">
                  Advanced algorithms extract tempo, pitch, rhythm, and musical patterns
                </p>
              </div>
              
              <div className="text-center">
                <div className="bg-white rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4 shadow-lg">
                  <Music className="h-8 w-8 text-purple-600" />
                </div>
                <h3 className="font-semibold text-lg mb-2">Smart Recommendations</h3>
                <p className="text-gray-600">
                  Get personalized song suggestions based on musical DNA analysis
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
