"use client";

import { useState, useCallback } from "react";
import type { ToastMessage, ToastType } from "@/app/components/error/Toast";

export function useToast() {
  const [toast, setToast] = useState<ToastMessage | null>(null);

  const showToast = useCallback((type: ToastType, title: string, message: string) => {
    const id = Math.random().toString(36).substring(7);
    setToast({ id, type, title, message });
  }, []);

  const showSuccess = useCallback(
    (title: string, message: string) => {
      showToast("success", title, message);
    },
    [showToast],
  );

  const showError = useCallback(
    (title: string, message: string) => {
      showToast("error", title, message);
    },
    [showToast],
  );

  const showWarning = useCallback(
    (title: string, message: string) => {
      showToast("warning", title, message);
    },
    [showToast],
  );

  const showInfo = useCallback(
    (title: string, message: string) => {
      showToast("info", title, message);
    },
    [showToast],
  );

  const hideToast = useCallback(() => {
    setToast(null);
  }, []);

  return {
    toast,
    showToast,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    hideToast,
  };
}
