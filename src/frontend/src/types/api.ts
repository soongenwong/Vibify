export interface MusicFeatures {
  pitch_range: {
    min: number;
    max: number;
    mean: number;
    std: number;
  };
  rhythm: {
    total_notes: number;
    avg_duration: number;
    duration_std: number;
    note_density: number;
  };
  dynamics: {
    avg_velocity: number;
    velocity_range: number;
    velocity_std: number;
  };
  temporal: {
    song_duration: number;
    onset_pattern: number[];
    tempo_estimate: number;
  };
  harmony: {
    pitch_classes: Record<string, number>;
    interval_distribution: Record<string, number>;
  };
}

export interface AnalysisResult {
  filename: string;
  file_size: number;
  features: MusicFeatures;
  status: string;
}

export interface RecommendationResult {
  filename: string;
  song_name: string;
  features: MusicFeatures;
  recommendations: string;
  status: string;
}

export interface ApiError {
  detail: string;
}
