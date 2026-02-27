"use client";

import { useState, useRef } from "react";
import { portfolioApi } from "@/app/lib/api/portfolio";
import { handleApiError } from "@/app/lib/api-client";

interface ImportPortfolioModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

interface ImportPreview {
  positions: Array<{
    ticker: string;
    quantity: number;
    purchase_price: number;
    purchase_date: string;
  }>;
  total_count: number;
}

interface ImportResult {
  success: boolean;
  imported_count: number;
  errors: string[];
  preview?: ImportPreview;
}

export default function ImportPortfolioModal({ isOpen, onClose, onSuccess }: ImportPortfolioModalProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [format, setFormat] = useState<"csv" | "excel">("csv");
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [validationErrors, setValidationErrors] = useState<string[]>([]);
  const [preview, setPreview] = useState<ImportPreview | null>(null);
  const [showPreview, setShowPreview] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setError(null);
      setValidationErrors([]);
      setPreview(null);
      setShowPreview(false);

      // Auto-detect format from file extension
      if (file.name.endsWith(".csv")) {
        setFormat("csv");
      } else if (file.name.endsWith(".xlsx") || file.name.endsWith(".xls")) {
        setFormat("excel");
      }
    }
  };

  const handlePreview = async () => {
    if (!selectedFile) return;

    try {
      setIsUploading(true);
      setError(null);
      setValidationErrors([]);

      const result: ImportResult = await portfolioApi.importPortfolio(selectedFile, format);

      if (result.errors && result.errors.length > 0) {
        setValidationErrors(result.errors);
        setShowPreview(false);
      } else if (result.preview) {
        setPreview(result.preview);
        setShowPreview(true);
      }
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setIsUploading(false);
    }
  };

  const handleConfirmImport = async () => {
    if (!selectedFile) return;

    try {
      setIsUploading(true);
      setError(null);

      const result: ImportResult = await portfolioApi.importPortfolio(selectedFile, format);

      if (result.success) {
        onSuccess();
        handleClose();
      } else if (result.errors && result.errors.length > 0) {
        setValidationErrors(result.errors);
      }
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setIsUploading(false);
    }
  };

  const handleClose = () => {
    setSelectedFile(null);
    setFormat("csv");
    setError(null);
    setValidationErrors([]);
    setPreview(null);
    setShowPreview(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50 p-4">
      <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="px-6 py-4 border-b border-[#2a2a2a] flex justify-between items-center">
          <h2 className="text-xl font-semibold text-white">Import Portfolio</h2>
          <button onClick={handleClose} className="text-gray-400 hover:text-white" disabled={isUploading}>
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="px-6 py-4">
          {/* File Upload Section */}
          {!showPreview && (
            <div className="space-y-4">
              {/* Format Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">File Format</label>
                <div className="flex gap-4">
                  <label className="flex items-center">
                    <input type="radio" value="csv" checked={format === "csv"} onChange={(e) => setFormat(e.target.value as "csv" | "excel")} className="mr-2 accent-blue-500" disabled={isUploading} />
                    <span className="text-sm text-gray-300">CSV</span>
                  </label>
                  <label className="flex items-center">
                    <input type="radio" value="excel" checked={format === "excel"} onChange={(e) => setFormat(e.target.value as "csv" | "excel")} className="mr-2 accent-blue-500" disabled={isUploading} />
                    <span className="text-sm text-gray-300">Excel</span>
                  </label>
                </div>
              </div>

              {/* File Input */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Select File</label>
                <div className="flex items-center gap-3">
                  <input ref={fileInputRef} type="file" accept={format === "csv" ? ".csv" : ".xlsx,.xls"} onChange={handleFileSelect} className="hidden" disabled={isUploading} />
                  <button onClick={() => fileInputRef.current?.click()} className="px-4 py-2 bg-[#2a2a2a] text-gray-300 rounded-lg hover:bg-[#333333] border border-[#3a3a3a]" disabled={isUploading}>
                    Choose File
                  </button>
                  {selectedFile && <span className="text-sm text-gray-400">{selectedFile.name}</span>}
                </div>
              </div>

              {/* Instructions */}
              <div className="bg-blue-900/20 border border-blue-800 rounded-lg p-4">
                <h3 className="text-sm font-medium text-blue-400 mb-2">File Format Requirements</h3>
                <ul className="text-sm text-blue-300 space-y-1 list-disc list-inside">
                  <li>File must contain columns: ticker, quantity, purchase_price, purchase_date</li>
                  <li>Ticker symbols must be valid US stock tickers</li>
                  <li>Quantity must be a positive number</li>
                  <li>Purchase price must be a positive number</li>
                  <li>Purchase date must be in YYYY-MM-DD format</li>
                </ul>
              </div>

              {/* Validation Errors */}
              {validationErrors.length > 0 && (
                <div className="bg-red-900/20 border border-red-800 rounded-lg p-4">
                  <h3 className="text-sm font-medium text-red-400 mb-2">Validation Errors</h3>
                  <ul className="text-sm text-red-300 space-y-1">
                    {validationErrors.map((error, index) => (
                      <li key={index} className="flex items-start gap-2">
                        <svg className="w-4 h-4 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                        </svg>
                        <span>{error}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* General Error */}
              {error && (
                <div className="bg-red-900/20 border border-red-800 rounded-lg p-4">
                  <p className="text-sm text-red-400">{error}</p>
                </div>
              )}
            </div>
          )}

          {/* Preview Section */}
          {showPreview && preview && (
            <div className="space-y-4">
              <div className="bg-green-900/20 border border-green-800 rounded-lg p-4">
                <h3 className="text-sm font-medium text-green-400 mb-1">Import Preview</h3>
                <p className="text-sm text-green-300">
                  Ready to import {preview.total_count} position{preview.total_count !== 1 ? "s" : ""}
                </p>
              </div>

              {/* Preview Table */}
              <div className="border border-[#2a2a2a] rounded-lg overflow-hidden">
                <div className="overflow-x-auto max-h-96">
                  <table className="w-full">
                    <thead className="bg-[#111111] sticky top-0">
                      <tr>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Ticker</th>
                        <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Quantity</th>
                        <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Purchase Price</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Purchase Date</th>
                      </tr>
                    </thead>
                    <tbody className="bg-[#1a1a1a] divide-y divide-[#2a2a2a]">
                      {preview.positions.map((position, index) => (
                        <tr key={index} className="hover:bg-[#222222]">
                          <td className="px-4 py-2 text-sm font-medium text-white">{position.ticker}</td>
                          <td className="px-4 py-2 text-sm text-gray-300 text-right">{position.quantity}</td>
                          <td className="px-4 py-2 text-sm text-gray-300 text-right">${position.purchase_price.toFixed(2)}</td>
                          <td className="px-4 py-2 text-sm text-gray-300">{position.purchase_date}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              <div className="bg-yellow-900/20 border border-yellow-800 rounded-lg p-4">
                <p className="text-sm text-yellow-300">
                  <strong>Note:</strong> Importing will add these positions to your existing portfolio. Duplicate positions will be added as separate entries.
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-[#2a2a2a] flex justify-end gap-3">
          <button onClick={handleClose} className="px-4 py-2 text-gray-300 bg-[#2a2a2a] rounded-lg hover:bg-[#333333]" disabled={isUploading}>
            Cancel
          </button>

          {!showPreview ? (
            <button onClick={handlePreview} disabled={!selectedFile || isUploading} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2">
              {isUploading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Validating...
                </>
              ) : (
                "Preview Import"
              )}
            </button>
          ) : (
            <>
              <button onClick={() => setShowPreview(false)} className="px-4 py-2 text-gray-300 bg-[#2a2a2a] rounded-lg hover:bg-[#333333]" disabled={isUploading}>
                Back
              </button>
              <button onClick={handleConfirmImport} disabled={isUploading} className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2">
                {isUploading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    Importing...
                  </>
                ) : (
                  <>
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    Confirm Import
                  </>
                )}
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
