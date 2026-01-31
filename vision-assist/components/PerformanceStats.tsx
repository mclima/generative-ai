'use client';

import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import type { PerformanceMetrics } from '@/types/detection';

interface PerformanceStatsProps {
  metrics: PerformanceMetrics;
}

export function PerformanceStats({ metrics }: PerformanceStatsProps) {
  return (
    <Card className="p-4 bg-black/80 border-gray-800">
      <div className="flex items-center gap-4 text-sm">
        <div className="flex items-center gap-2">
          <span className="text-gray-400">FPS:</span>
          <Badge variant={metrics.fps >= 20 ? 'default' : 'destructive'}>
            {metrics.fps}
          </Badge>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-gray-400">Inference:</span>
          <Badge variant="outline">{metrics.inferenceTime}ms</Badge>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-gray-400">Model:</span>
          <Badge variant={metrics.modelLoaded ? 'default' : 'secondary'}>
            {metrics.modelLoaded ? 'Loaded' : 'Loading...'}
          </Badge>
        </div>
      </div>
    </Card>
  );
}
