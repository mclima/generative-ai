"use client";

import { useEffect, useState } from "react";

interface SuccessCheckmarkProps {
  show: boolean;
  size?: "sm" | "md" | "lg";
  onComplete?: () => void;
  duration?: number;
}

export default function SuccessCheckmark({ show, size = "md", onComplete, duration = 2000 }: SuccessCheckmarkProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    if (show) {
      setIsVisible(true);
      setIsAnimating(true);

      const timer = setTimeout(() => {
        setIsAnimating(false);
        setTimeout(() => {
          setIsVisible(false);
          if (onComplete) onComplete();
        }, 300);
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [show, duration, onComplete]);

  if (!isVisible) return null;

  const sizeClasses = {
    sm: "w-12 h-12",
    md: "w-16 h-16",
    lg: "w-24 h-24",
  };

  const checkmarkSizes = {
    sm: "w-6 h-6",
    md: "w-8 h-8",
    lg: "w-12 h-12",
  };

  return (
    <div className={`fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-30 transition-opacity duration-300 ${isAnimating ? "opacity-100" : "opacity-0"}`}>
      <div className={`${sizeClasses[size]} bg-green-500 rounded-full flex items-center justify-center shadow-lg transform transition-all duration-500 ${isAnimating ? "scale-100 rotate-0" : "scale-0 rotate-180"}`}>
        <svg className={`${checkmarkSizes[size]} text-white animate-draw-check`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
        </svg>
      </div>
      <style jsx>{`
        @keyframes draw-check {
          0% {
            stroke-dasharray: 0, 100;
          }
          100% {
            stroke-dasharray: 100, 0;
          }
        }
        .animate-draw-check {
          animation: draw-check 0.5s ease-in-out forwards;
        }
      `}</style>
    </div>
  );
}
