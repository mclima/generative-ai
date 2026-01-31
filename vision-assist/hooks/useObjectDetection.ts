import { useState, useEffect, useCallback, useRef } from 'react';
import type { DetectedObject, PerformanceMetrics, DetectionSettings } from '@/types/detection';
import { loadModel, getModel } from '@/lib/detection';
import * as tf from '@tensorflow/tfjs';

export function useObjectDetection(settings: DetectionSettings) {
  const [isModelLoading, setIsModelLoading] = useState(false);
  const [modelError, setModelError] = useState<string | null>(null);
  const [detections, setDetections] = useState<DetectedObject[]>([]);
  const [metrics, setMetrics] = useState<PerformanceMetrics>({
    fps: 0,
    inferenceTime: 0,
    modelLoaded: false,
  });

  const frameCount = useRef(0);
  const lastTime = useRef(Date.now());
  const animationFrameId = useRef<number | undefined>(undefined);

  useEffect(() => {
    let mounted = true;

    async function initModel() {
      setIsModelLoading(true);
      setModelError(null);
      
      try {
        const backend = tf.getBackend();
        if (backend !== 'webgl') {
          await tf.setBackend('webgl');
        }
        await loadModel();
        if (mounted) {
          setMetrics(prev => ({ ...prev, modelLoaded: true }));
          setIsModelLoading(false);
        }
      } catch (error) {
        if (mounted) {
          setModelError(error instanceof Error ? error.message : 'Failed to load model');
          setIsModelLoading(false);
        }
      }
    }

    initModel();

    return () => {
      mounted = false;
    };
  }, []);

  const detect = useCallback(async (
    videoElement: HTMLVideoElement | null
  ): Promise<DetectedObject[]> => {
    if (!videoElement || videoElement.readyState !== 4) {
      return [];
    }

    if (videoElement.videoWidth === 0 || videoElement.videoHeight === 0) {
      return [];
    }

    const model = getModel();
    if (!model) {
      return [];
    }

    const startTime = performance.now();
    
    try {
      const predictions = await model.detect(videoElement);
      const inferenceTime = performance.now() - startTime;

      const filtered = predictions
        .filter(pred => pred.score >= settings.confidenceThreshold)
        .map(pred => ({
          bbox: pred.bbox as [number, number, number, number],
          class: pred.class,
          score: pred.score,
        }));

      frameCount.current++;
      const now = Date.now();
      const elapsed = now - lastTime.current;

      if (elapsed >= 1000) {
        const fps = (frameCount.current * 1000) / elapsed;
        setMetrics(prev => ({
          ...prev,
          fps: Math.round(fps),
          inferenceTime: Math.round(inferenceTime),
        }));
        frameCount.current = 0;
        lastTime.current = now;
      }

      return filtered;
    } catch (error) {
      console.error('Detection error:', error);
      return [];
    }
  }, [settings.confidenceThreshold]);

  const startDetection = useCallback((
    videoElement: HTMLVideoElement | null,
    onDetect: (detections: DetectedObject[]) => void
  ) => {
    if (!videoElement) return;

    const detectFrame = async () => {
      const results = await detect(videoElement);
      onDetect(results);
      setDetections(results);
      
      animationFrameId.current = requestAnimationFrame(detectFrame);
    };

    detectFrame();
  }, [detect]);

  const stopDetection = useCallback(() => {
    if (animationFrameId.current) {
      cancelAnimationFrame(animationFrameId.current);
      animationFrameId.current = undefined;
    }
  }, []);

  return {
    isModelLoading,
    modelError,
    detections,
    metrics,
    detect,
    startDetection,
    stopDetection,
  };
}
