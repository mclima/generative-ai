"use client";

interface ProgressIndicatorProps {
  progress: number; // 0-100
  label?: string;
  showPercentage?: boolean;
  size?: "sm" | "md" | "lg";
  color?: "blue" | "green" | "orange";
  className?: string;
}

export default function ProgressIndicator({ progress, label, showPercentage = true, size = "md", color = "blue", className = "" }: ProgressIndicatorProps) {
  const clampedProgress = Math.min(Math.max(progress, 0), 100);

  const heightClasses = {
    sm: "h-1",
    md: "h-2",
    lg: "h-3",
  };

  const colorClasses = {
    blue: "bg-blue-600",
    green: "bg-green-600",
    orange: "bg-orange-600",
  };

  return (
    <div className={`w-full ${className}`}>
      {(label || showPercentage) && (
        <div className="flex items-center justify-between mb-2">
          {label && <span className="text-sm font-medium text-gray-700">{label}</span>}
          {showPercentage && <span className="text-sm font-medium text-gray-700">{Math.round(clampedProgress)}%</span>}
        </div>
      )}
      <div className={`w-full bg-gray-200 rounded-full overflow-hidden ${heightClasses[size]}`}>
        <div className={`${heightClasses[size]} ${colorClasses[color]} rounded-full transition-all duration-300 ease-out`} style={{ width: `${clampedProgress}%` }} />
      </div>
    </div>
  );
}
