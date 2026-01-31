'use client';

import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Slider } from '@/components/ui/slider';
import { Play, Pause, Volume2, VolumeX } from 'lucide-react';
import type { DetectionSettings } from '@/types/detection';

interface ControlPanelProps {
  isDetecting: boolean;
  isModelLoading: boolean;
  isWebcamActive: boolean;
  settings: DetectionSettings;
  onToggleDetection: () => void;
  onStopAll: () => void;
  onSettingsChange: (settings: Partial<DetectionSettings>) => void;
}

export function ControlPanel({
  isDetecting,
  isModelLoading,
  isWebcamActive,
  settings,
  onToggleDetection,
  onStopAll,
  onSettingsChange,
}: ControlPanelProps) {
  const getButtonText = () => {
    if (isDetecting) return { icon: Pause, text: 'Stop Detection' };
    if (isWebcamActive) return { icon: Play, text: 'Start Detection' };
    return { icon: Play, text: 'Activate Camera' };
  };

  const { icon: Icon, text } = getButtonText();

  return (
    <Card className="p-6 bg-black/80 border-gray-800">
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-white">Controls</h3>
          <div className="flex gap-2 flex-wrap">
            <Button
              onClick={onToggleDetection}
              disabled={isModelLoading}
              size="lg"
              className="gap-2"
            >
              <Icon className="w-4 h-4" />
              {text}
            </Button>
            {(isWebcamActive || isDetecting) && (
              <Button
                onClick={onStopAll}
                variant="outline"
                size="lg"
              >
                Stop All
              </Button>
            )}
          </div>
        </div>

        <div className="space-y-4">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-sm text-gray-300">
                Confidence Threshold
              </label>
              <span className="text-sm text-gray-400">
                {Math.round(settings.confidenceThreshold * 100)}%
              </span>
            </div>
            <Slider
              value={[settings.confidenceThreshold]}
              onValueChange={([value]) =>
                onSettingsChange({ confidenceThreshold: value })
              }
              min={0.1}
              max={0.9}
              step={0.05}
              className="w-full"
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              {settings.enableAudio ? (
                <Volume2 className="w-4 h-4 text-gray-400" />
              ) : (
                <VolumeX className="w-4 h-4 text-gray-400" />
              )}
              <label className="text-sm text-gray-300">Audio Feedback</label>
            </div>
            <Switch
              checked={settings.enableAudio}
              onCheckedChange={(checked) =>
                onSettingsChange({ enableAudio: checked })
              }
            />
          </div>
        </div>
      </div>
    </Card>
  );
}
