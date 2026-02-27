"use client";

interface ConfirmDialogProps {
  isOpen: boolean;
  title: string;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  onConfirm: () => void;
  onCancel: () => void;
  isDestructive?: boolean;
}

export default function ConfirmDialog({ isOpen, title, message, confirmLabel = "Confirm", cancelLabel = "Cancel", onConfirm, onCancel, isDestructive = false }: ConfirmDialogProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg shadow-xl max-w-md w-full">
        <div className="p-6">
          <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>
          <p className="text-gray-400 mb-6">{message}</p>

          <div className="flex gap-3">
            <button onClick={onCancel} className="flex-1 px-4 py-2 border border-[#2a2a2a] text-gray-300 rounded-lg hover:bg-[#2a2a2a]">
              {cancelLabel}
            </button>
            <button onClick={onConfirm} className={`flex-1 px-4 py-2 rounded-lg text-white ${isDestructive ? "bg-red-600 hover:bg-red-700" : "bg-blue-600 hover:bg-blue-700"}`}>
              {confirmLabel}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
