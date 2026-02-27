"use client";

interface SkeletonLoaderProps {
  variant?: "portfolio" | "chart" | "news" | "text" | "card";
  count?: number;
  className?: string;
}

export default function SkeletonLoader({ variant = "text", count = 1, className = "" }: SkeletonLoaderProps) {
  const renderSkeleton = () => {
    switch (variant) {
      case "portfolio":
        return (
          <div className="space-y-4">
            {/* Portfolio header skeleton */}
            <div className="bg-white rounded-lg shadow p-6 space-y-4">
              <div className="h-8 bg-gray-200 rounded w-1/3 animate-pulse" />
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="h-20 bg-gray-200 rounded animate-pulse" />
                <div className="h-20 bg-gray-200 rounded animate-pulse" />
                <div className="h-20 bg-gray-200 rounded animate-pulse" />
              </div>
            </div>
            {/* Portfolio positions skeleton */}
            <div className="bg-white rounded-lg shadow overflow-hidden">
              <div className="p-4 border-b">
                <div className="h-6 bg-gray-200 rounded w-1/4 animate-pulse" />
              </div>
              {[...Array(5)].map((_, i) => (
                <div key={i} className="p-4 border-b last:border-b-0 flex items-center justify-between">
                  <div className="flex-1 space-y-2">
                    <div className="h-5 bg-gray-200 rounded w-1/4 animate-pulse" />
                    <div className="h-4 bg-gray-200 rounded w-1/3 animate-pulse" />
                  </div>
                  <div className="space-y-2">
                    <div className="h-5 bg-gray-200 rounded w-20 animate-pulse" />
                    <div className="h-4 bg-gray-200 rounded w-16 animate-pulse" />
                  </div>
                </div>
              ))}
            </div>
          </div>
        );

      case "chart":
        return (
          <div className="bg-white rounded-lg shadow p-6">
            <div className="h-6 bg-gray-200 rounded w-1/3 mb-4 animate-pulse" />
            <div className="h-64 bg-gray-200 rounded animate-pulse" />
            <div className="flex gap-2 mt-4">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="h-8 bg-gray-200 rounded w-16 animate-pulse" />
              ))}
            </div>
          </div>
        );

      case "news":
        return (
          <div className="space-y-4">
            {[...Array(count)].map((_, i) => (
              <div key={i} className="bg-white rounded-lg shadow p-4 space-y-3">
                <div className="flex items-start gap-3">
                  <div className="h-16 w-16 bg-gray-200 rounded animate-pulse flex-shrink-0" />
                  <div className="flex-1 space-y-2">
                    <div className="h-5 bg-gray-200 rounded w-3/4 animate-pulse" />
                    <div className="h-4 bg-gray-200 rounded w-full animate-pulse" />
                    <div className="h-4 bg-gray-200 rounded w-2/3 animate-pulse" />
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="h-4 bg-gray-200 rounded w-24 animate-pulse" />
                  <div className="h-4 bg-gray-200 rounded w-20 animate-pulse" />
                </div>
              </div>
            ))}
          </div>
        );

      case "card":
        return (
          <div className="bg-white rounded-lg shadow p-6 space-y-4">
            <div className="h-6 bg-gray-200 rounded w-1/2 animate-pulse" />
            <div className="h-4 bg-gray-200 rounded w-full animate-pulse" />
            <div className="h-4 bg-gray-200 rounded w-5/6 animate-pulse" />
            <div className="h-4 bg-gray-200 rounded w-4/6 animate-pulse" />
          </div>
        );

      case "text":
      default:
        return (
          <div className="space-y-2">
            {[...Array(count)].map((_, i) => (
              <div key={i} className="h-4 bg-gray-200 rounded animate-pulse" style={{ width: `${Math.random() * 30 + 70}%` }} />
            ))}
          </div>
        );
    }
  };

  return <div className={className}>{renderSkeleton()}</div>;
}
