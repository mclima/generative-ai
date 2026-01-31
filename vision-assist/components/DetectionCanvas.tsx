'use client';

import { useEffect, useRef } from 'react';
import type { DetectedObject } from '@/types/detection';

interface DetectionCanvasProps {
  detections: DetectedObject[];
  videoWidth: number;
  videoHeight: number;
}

const COLORS = [
  '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
  '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B739', '#52B788'
];

export function DetectionCanvas({ detections, videoWidth, videoHeight }: DetectionCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    detections.forEach((detection, index) => {
      const [x, y, width, height] = detection.bbox;
      const color = COLORS[index % COLORS.length];

      ctx.strokeStyle = color;
      ctx.lineWidth = 3;
      ctx.strokeRect(x, y, width, height);

      ctx.fillStyle = color;
      ctx.fillRect(x, y - 30, width, 30);

      ctx.fillStyle = '#000000';
      ctx.font = 'bold 16px sans-serif';
      ctx.fillText(
        `${detection.class} ${Math.round(detection.score * 100)}%`,
        x + 5,
        y - 8
      );
    });
  }, [detections]);

  return (
    <canvas
      ref={canvasRef}
      width={videoWidth}
      height={videoHeight}
      className="absolute top-0 left-0 w-full h-full pointer-events-none"
    />
  );
}
