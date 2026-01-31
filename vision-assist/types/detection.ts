export interface DetectedObject {
  bbox: [number, number, number, number];
  class: string;
  score: number;
}

export interface PerformanceMetrics {
  fps: number;
  inferenceTime: number;
  modelLoaded: boolean;
}

export interface DetectionSettings {
  confidenceThreshold: number;
  enableAudio: boolean;
  maxFps: number;
}
