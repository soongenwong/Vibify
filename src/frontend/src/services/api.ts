import axios from 'axios';
import type { AnalysisResult, RecommendationResult, ApiError } from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minutes for audio processing
});

export const analyzeMusic = async (file: File): Promise<AnalysisResult> => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await api.post<AnalysisResult>('/analyze', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response?.data) {
      const apiError = error.response.data as ApiError;
      throw new Error(apiError.detail || 'Failed to analyze music');
    }
    throw new Error('Network error occurred');
  }
};

export const getRecommendations = async (
  file: File, 
  songName?: string
): Promise<RecommendationResult> => {
  const formData = new FormData();
  formData.append('file', file);
  if (songName) {
    formData.append('song_name', songName);
  }

  try {
    const response = await api.post<RecommendationResult>('/recommend', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response?.data) {
      const apiError = error.response.data as ApiError;
      throw new Error(apiError.detail || 'Failed to get recommendations');
    }
    throw new Error('Network error occurred');
  }
};

export const getHealthStatus = async (): Promise<{ status: string; api_key_configured: boolean }> => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    throw new Error('Failed to check API health');
  }
};
