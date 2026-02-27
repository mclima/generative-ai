"use client";

interface ErrorMessageProps {
  title?: string;
  message: string;
  onRetry?: () => void;
  variant?: "error" | "warning" | "info";
  className?: string;
}

export default function ErrorMessage({ title = "Error", message, onRetry, variant = "error", className = "" }: ErrorMessageProps) {
  const variantStyles = {
    error: {
      container: "bg-red-50 border-red-200",
      icon: "text-red-600",
      title: "text-red-800",
      message: "text-red-700",
      button: "bg-red-600 hover:bg-red-700",
    },
    warning: {
      container: "bg-orange-50 border-orange-200",
      icon: "text-orange-600",
      title: "text-orange-800",
      message: "text-orange-700",
      button: "bg-orange-600 hover:bg-orange-700",
    },
    info: {
      container: "bg-blue-50 border-blue-200",
      icon: "text-blue-600",
      title: "text-blue-800",
      message: "text-blue-700",
      button: "bg-blue-600 hover:bg-blue-700",
    },
  };

  const styles = variantStyles[variant];

  const getIcon = () => {
    if (variant === "warning") {
      return (
        <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      );
    }
    if (variant === "info") {
      return (
        <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      );
    }
    return (
      <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    );
  };

  return (
    <div className={`border-2 rounded-lg p-4 ${styles.container} ${className}`}>
      <div className="flex items-start">
        <div className={`flex-shrink-0 ${styles.icon}`}>{getIcon()}</div>
        <div className="ml-3 flex-1">
          <h3 className={`text-sm font-medium ${styles.title}`}>{title}</h3>
          <p className={`mt-1 text-sm ${styles.message}`}>{message}</p>
          {onRetry && (
            <button onClick={onRetry} className={`mt-3 px-4 py-2 text-sm font-medium text-white rounded-lg transition-colors ${styles.button}`}>
              Try Again
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
