import { useState, useCallback, useRef } from 'react';

export function useWebcam() {
  const [isActive, setIsActive] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const startWebcam = useCallback(async () => {
    try {
      // Check if mediaDevices is supported
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('Camera access not supported on this browser');
      }

      // Try with ideal constraints first
      let stream: MediaStream;
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          video: {
            facingMode: 'environment',
            width: { ideal: 1280 },
            height: { ideal: 720 },
          },
        });
      } catch (err) {
        // Fallback to basic constraints for mobile compatibility
        console.warn('Failed with ideal constraints, trying basic constraints:', err);
        stream = await navigator.mediaDevices.getUserMedia({
          video: {
            facingMode: 'environment',
          },
        });
      }
      
      streamRef.current = stream;
      setIsActive(true);
      setError(null);
      console.log('Webcam started successfully');
      return stream;
    } catch (err) {
      console.error('Webcam error:', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to access webcam';
      setError(errorMessage);
      setIsActive(false);
      throw err;
    }
  }, []);

  const stopWebcam = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    setIsActive(false);
  }, []);

  return {
    isActive,
    error,
    startWebcam,
    stopWebcam,
  };
}
