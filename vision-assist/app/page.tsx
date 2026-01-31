'use client';

import { useState, useRef, useCallback } from 'react';
import Webcam from 'react-webcam';
import { WebcamView } from '@/components/WebcamView';
import { DetectionCanvas } from '@/components/DetectionCanvas';
import { PerformanceStats } from '@/components/PerformanceStats';
import { ControlPanel } from '@/components/ControlPanel';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useObjectDetection } from '@/hooks/useObjectDetection';
import { useWebcam } from '@/hooks/useWebcam';
import type { DetectionSettings, DetectedObject } from '@/types/detection';
import { Eye, AlertCircle } from 'lucide-react';

export default function Home() {
  const webcamRef = useRef<Webcam>(null);
  const [videoElement, setVideoElement] = useState<HTMLVideoElement | null>(null);
  const [isDetecting, setIsDetecting] = useState(false);
  const [detections, setDetections] = useState<DetectedObject[]>([]);
  const [settings, setSettings] = useState<DetectionSettings>({
    confidenceThreshold: 0.5,
    enableAudio: true,
    maxFps: 30,
  });
  const lastAnnouncementRef = useRef<string>('');
  const lastAnnouncementTimeRef = useRef<number>(0);
  const audioEnabledRef = useRef<boolean>(true);

  const { isActive: isWebcamActive, error: webcamError, startWebcam, stopWebcam } = useWebcam();
  const {
    isModelLoading,
    modelError,
    metrics,
    startDetection,
    stopDetection,
  } = useObjectDetection(settings);

  const handleVideoReady = useCallback((video: HTMLVideoElement) => {
    setVideoElement(video);
  }, []);

  const handleToggleDetection = useCallback(async () => {
    if (isDetecting) {
      stopDetection();
      speechSynthesis.cancel();
      lastAnnouncementRef.current = '';
      lastAnnouncementTimeRef.current = 0;
      setIsDetecting(false);
      setDetections([]);
    } else if (isWebcamActive && videoElement) {
      audioEnabledRef.current = true;
      lastAnnouncementRef.current = '';
      lastAnnouncementTimeRef.current = 0;
      setSettings(prev => ({ ...prev, enableAudio: true }));
      
      setTimeout(() => {
        if (videoElement.videoWidth > 0 && videoElement.videoHeight > 0) {
          startDetection(videoElement, (newDetections) => {
            setDetections(newDetections);
            
            if (audioEnabledRef.current && newDetections.length > 0) {
              const objectNames = newDetections.map(d => d.class).sort().join(', ');
              const now = Date.now();
              
              if (objectNames !== lastAnnouncementRef.current || now - lastAnnouncementTimeRef.current > 5000) {
                lastAnnouncementRef.current = objectNames;
                lastAnnouncementTimeRef.current = now;
                
                if (speechSynthesis.speaking) {
                  speechSynthesis.cancel();
                }
                
                setTimeout(() => {
                  const text = `Detected ${objectNames.replace(/,/g, ' and')}`;
                  const utterance = new SpeechSynthesisUtterance(text);
                  utterance.volume = 1.0;
                  utterance.lang = 'en-US';
                  speechSynthesis.speak(utterance);
                }, 100);
              }
            }
          });
          setIsDetecting(true);
        }
      }, 100);
    } else {
      try {
        await startWebcam();
      } catch (error) {
        console.error('Failed to start webcam:', error);
      }
    }
  }, [isDetecting, isWebcamActive, videoElement, settings.enableAudio, startWebcam, startDetection, stopDetection]);

  const handleStopAll = useCallback(() => {
    stopDetection();
    stopWebcam();
    speechSynthesis.cancel();
    lastAnnouncementRef.current = '';
    lastAnnouncementTimeRef.current = 0;
    audioEnabledRef.current = false;
    setIsDetecting(false);
    setDetections([]);
    setSettings(prev => ({ ...prev, enableAudio: false }));
  }, [stopDetection, stopWebcam]);

  const handleSettingsChange = useCallback((newSettings: Partial<DetectionSettings>) => {
    setSettings(prev => ({ ...prev, ...newSettings }));
    if (newSettings.enableAudio !== undefined) {
      audioEnabledRef.current = newSettings.enableAudio;
    }
  }, []);

  return (
    <div className="min-h-screen bg-black text-white">
      <header className="border-b border-gray-800 bg-black/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Eye className="w-8 h-8 text-blue-500" />
              <div>
                <h1 className="text-2xl font-bold">VisionAssist</h1>
                <p className="text-sm text-gray-400">Assistive Object Detection for the Visually Impaired</p>
              </div>
            </div>
            <PerformanceStats metrics={metrics} />
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-6">
        {(webcamError || modelError) && (
          <Alert variant="destructive" className="mb-4">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              {webcamError || modelError}
            </AlertDescription>
          </Alert>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <div className="relative aspect-video bg-gray-900 rounded-lg overflow-hidden">
              <WebcamView
                ref={webcamRef}
                isActive={isWebcamActive}
                onReady={handleVideoReady}
              />
              {isWebcamActive && videoElement && (
                <DetectionCanvas
                  detections={detections}
                  videoWidth={videoElement.videoWidth || 1280}
                  videoHeight={videoElement.videoHeight || 720}
                />
              )}
            </div>

            {detections.length > 0 && (
              <div className="mt-4 p-4 bg-gray-900 rounded-lg">
                <h3 className="text-sm font-semibold mb-2 text-gray-300">
                  Detected Objects ({detections.length})
                </h3>
                <div className="flex flex-wrap gap-2">
                  {detections.map((detection, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-blue-500/20 text-blue-300 rounded-full text-sm"
                    >
                      {detection.class} ({Math.round(detection.score * 100)}%)
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="space-y-6">
            <ControlPanel
              isDetecting={isDetecting}
              isModelLoading={isModelLoading}
              isWebcamActive={isWebcamActive}
              settings={settings}
              onToggleDetection={handleToggleDetection}
              onStopAll={handleStopAll}
              onSettingsChange={handleSettingsChange}
            />

            <div className="p-6 bg-gray-900 rounded-lg border border-gray-800">
              <h3 className="text-lg font-semibold mb-3">About</h3>
              <p className="text-sm text-gray-400 leading-relaxed">
                VisionAssist uses TensorFlow.js and the COCO-SSD model to detect objects in real-time. 
                All processing happens in your browser - no data is sent to any server.
              </p>
              <div className="mt-4 pt-4 border-t border-gray-800 space-y-3">
                <p className="text-xs text-gray-500">
                  Detects 90 common objects including people, vehicles, animals, and household items.
                </p>
                <div className="text-xs text-gray-500">
                  <p className="font-semibold text-gray-400 mb-1">Detection Tips:</p>
                  <ul className="space-y-1 list-disc list-inside">
                    <li>Small objects (spoons, keys, phones) may require good lighting and closer proximity</li>
                    <li>Lower the confidence threshold to 30-40% for better small object detection</li>
                    <li>Ensure objects are fully visible and not partially hidden</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      <footer className="border-t border-gray-800 mt-12">
        <div className="container mx-auto px-4 py-6 text-center text-sm text-gray-500">
          <p>Privacy-first • All processing happens locally in your browser</p>
        </div>
      </footer>
    </div>
  );
}
