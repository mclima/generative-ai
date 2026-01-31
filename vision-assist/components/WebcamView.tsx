'use client';

import { useRef, useEffect, forwardRef } from 'react';
import Webcam from 'react-webcam';

interface WebcamViewProps {
  onReady?: (video: HTMLVideoElement) => void;
  isActive: boolean;
}

export const WebcamView = forwardRef<Webcam, WebcamViewProps>(
  ({ onReady, isActive }, ref) => {
    const videoRef = useRef<HTMLVideoElement | null>(null);

    useEffect(() => {
      if (ref && typeof ref !== 'function' && ref.current) {
        const video = ref.current.video;
        if (video && onReady) {
          videoRef.current = video;
          onReady(video);
        }
      }
    }, [ref, onReady, isActive]);

    return (
      <div className="relative w-full h-full flex items-center justify-center bg-black">
        {isActive ? (
          <Webcam
            ref={ref}
            audio={false}
            screenshotFormat="image/jpeg"
            videoConstraints={{
              facingMode: 'environment',
              width: { ideal: 1280 },
              height: { ideal: 720 },
            }}
            className="w-full h-full object-contain"
          />
        ) : (
          <div className="text-gray-400 text-center p-8">
            <p className="text-lg">Camera not active</p>
            <p className="text-sm mt-2">Click "Start Detection" to begin</p>
          </div>
        )}
      </div>
    );
  }
);

WebcamView.displayName = 'WebcamView';
