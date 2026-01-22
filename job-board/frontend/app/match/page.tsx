"use client";

import { useState } from "react";
import Link from "next/link";

type ResumeAnalysis = {
  skills: string[];
  years_experience: number;
  preferred_roles: string[];
  seniority: string;
  strengths: string[];
};

type MatchedJob = {
  id: number;
  title: string;
  company: string;
  location: string;
  remote: boolean;
  role: string;
  source: string;
  url: string;
  posted_date: string;
  salary?: string;
  match_score: number;
  match_percentage: number;
  matched_skills: string[];
  match_explanation: string;
};

type MatchResponse = {
  resume_analysis: ResumeAnalysis;
  matched_jobs: MatchedJob[];
  total_matches: number;
};

export default function MatchPage() {
  const [resumeText, setResumeText] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [inputMode, setInputMode] = useState<"paste" | "upload">("paste");
  const [loading, setLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState("");
  const [results, setResults] = useState<MatchResponse | null>(null);
  const [error, setError] = useState("");

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
      if (!validTypes.includes(file.type)) {
        setError("Please upload a PDF, DOCX, or TXT file");
        return;
      }
      setSelectedFile(file);
      setError("");
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (inputMode === "paste") {
      if (!resumeText.trim()) {
        setError("Please paste your resume text");
        return;
      }
      if (resumeText.trim().length < 100) {
        setError("Resume seems too short. Please paste your full resume (at least 100 characters)");
        return;
      }
    } else {
      if (!selectedFile) {
        setError("Please select a file to upload");
        return;
      }
    }

    setLoading(true);
    setError("");
    setResults(null);

    try {
      setLoadingMessage("Analyzing your resume...");
      await new Promise(resolve => setTimeout(resolve, 500));
      
      let response;
      
      if (inputMode === "paste") {
        response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "https://generative-ai-production-621e.up.railway.app"}/jobs/match`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ resume_text: resumeText }),
        });
      } else {
        const formData = new FormData();
        formData.append("file", selectedFile!);
        
        response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "https://generative-ai-production-621e.up.railway.app"}/jobs/match/upload`, {
          method: "POST",
          body: formData,
        });
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Failed to match resume");
      }

      setLoadingMessage("Matching with jobs...");
      const data = await response.json();
      
      setLoadingMessage("Ranking results...");
      await new Promise(resolve => setTimeout(resolve, 300));
      
      setResults(data);
      
      // Scroll to results
      setTimeout(() => {
        document.getElementById("results-section")?.scrollIntoView({ behavior: "smooth" });
      }, 100);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message.includes("fetch") 
          ? "Cannot connect to server. Please make sure the backend is running." 
          : err.message);
      } else {
        setError("Failed to analyze resume. Please try again.");
      }
      console.error(err);
    } finally {
      setLoading(false);
      setLoadingMessage("");
    }
  };

  const handleClear = () => {
    setResumeText("");
    setSelectedFile(null);
    setResults(null);
    setError("");
  };

  const getMatchColor = (percentage: number) => {
    if (percentage >= 70) return "#10b981";
    if (percentage >= 40) return "#f59e0b";
    return "#6b7280";
  };

  return (
    <div className="jobs-container">
      <div style={{ marginBottom: "2rem" }}>
        <Link href="/" style={{ color: "#3b82f6", textDecoration: "none" }}>
          ← Back to Jobs
        </Link>
      </div>

      <h1 className="jobs-title">Resume Matcher</h1>
      <p style={{ color: "#9ca3af", marginBottom: "1rem" }}>
        Upload your resume or paste the text below and we'll match you with relevant jobs using AI (showing matches 60% and above)
      </p>
      <p style={{ color: "#3b82f6", fontSize: "0.875rem", marginBottom: "1rem", padding: "0.75rem", backgroundColor: "#1a1a1a", borderRadius: "6px", border: "1px solid #1e3a8a" }}>
        💡 <strong>Tip:</strong> For best results, use an ATS-compatible resume format (plain text, clear headings, standard fonts, no complex formatting or graphics).
      </p>

      <form onSubmit={handleSubmit} style={{ marginBottom: "3rem" }}>
        {/* Tabs for input mode */}
        <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem", borderBottom: "1px solid #333" }}>
          <button
            type="button"
            onClick={() => setInputMode("paste")}
            style={{
              padding: "0.75rem 1.5rem",
              backgroundColor: "transparent",
              color: inputMode === "paste" ? "#3b82f6" : "#9ca3af",
              border: "none",
              borderBottom: inputMode === "paste" ? "2px solid #3b82f6" : "2px solid transparent",
              cursor: "pointer",
              fontWeight: inputMode === "paste" ? "600" : "400",
            }}
          >
            📝 Paste Text
          </button>
          <button
            type="button"
            onClick={() => setInputMode("upload")}
            style={{
              padding: "0.75rem 1.5rem",
              backgroundColor: "transparent",
              color: inputMode === "upload" ? "#3b82f6" : "#9ca3af",
              border: "none",
              borderBottom: inputMode === "upload" ? "2px solid #3b82f6" : "2px solid transparent",
              cursor: "pointer",
              fontWeight: inputMode === "upload" ? "600" : "400",
            }}
          >
            📄 Upload File
          </button>
        </div>

        {inputMode === "paste" ? (
          <div style={{ position: "relative" }}>
            <textarea
              value={resumeText}
              onChange={(e) => setResumeText(e.target.value)}
              placeholder="Paste your resume here in text format"
              disabled={loading}
              style={{
                width: "100%",
                minHeight: "300px",
                padding: "1rem",
                backgroundColor: "#1a1a1a",
                border: "1px solid #333",
                borderRadius: "8px",
                color: "#e5e7eb",
                fontSize: "0.875rem",
                fontFamily: "monospace",
                resize: "vertical",
                opacity: loading ? 0.6 : 1,
              }}
            />
            <div style={{ 
              position: "absolute", 
              bottom: "0.5rem", 
              right: "0.5rem", 
              fontSize: "0.75rem", 
              color: "#6b7280",
              backgroundColor: "#1a1a1a",
              padding: "0.25rem 0.5rem",
              borderRadius: "4px"
            }}>
              {resumeText.length} characters
            </div>
          </div>
        ) : (
          <div style={{
            padding: "2rem",
            backgroundColor: "#1a1a1a",
            border: "2px dashed #333",
            borderRadius: "8px",
            textAlign: "left",
          }}>
            <input
              type="file"
              accept=".pdf,.docx,.txt"
              onChange={handleFileChange}
              disabled={loading}
              style={{ display: "none" }}
              id="file-upload"
            />
            <label
              htmlFor="file-upload"
              style={{
                display: "inline-block",
                padding: "0.75rem 1.5rem",
                backgroundColor: "#3b82f6",
                color: "white",
                borderRadius: "6px",
                cursor: loading ? "not-allowed" : "pointer",
                fontWeight: "600",
                opacity: loading ? 0.6 : 1,
              }}
            >
              Choose File
            </label>
            <p style={{ color: "#9ca3af", marginTop: "1rem", fontSize: "0.875rem" }}>
              Supported formats: PDF, DOCX, TXT
            </p>
            {selectedFile && (
              <div style={{
                marginTop: "1rem",
                padding: "0.75rem",
                backgroundColor: "#0f0f0f",
                borderRadius: "6px",
                display: "inline-block",
              }}>
                <span style={{ color: "#10b981" }}>✓</span> {selectedFile.name}
                <button
                  type="button"
                  onClick={() => setSelectedFile(null)}
                  style={{
                    marginLeft: "0.5rem",
                    color: "#ef4444",
                    background: "none",
                    border: "none",
                    cursor: "pointer",
                    fontSize: "1rem",
                  }}
                >
                  ✕
                </button>
              </div>
            )}
          </div>
        )}
        
        <div style={{ display: "flex", gap: "1rem", marginTop: "1rem", flexWrap: "wrap" }}>
          <button
            type="submit"
            disabled={loading}
            style={{
              padding: "0.75rem 2rem",
              backgroundColor: loading ? "#555" : "#3b82f6",
              color: "white",
              border: "none",
              borderRadius: "6px",
              fontSize: "1rem",
              fontWeight: "600",
              cursor: loading ? "not-allowed" : "pointer",
              transition: "background-color 0.2s",
            }}
          >
            {loading ? (
              <span style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <span style={{ 
                  display: "inline-block",
                  width: "16px",
                  height: "16px",
                  border: "2px solid #fff",
                  borderTopColor: "transparent",
                  borderRadius: "50%",
                  animation: "spin 0.8s linear infinite"
                }}></span>
                {loadingMessage || "Analyzing..."}
              </span>
            ) : "Find Matching Jobs"}
          </button>
          
          {(resumeText || selectedFile) && !loading && (
            <button
              type="button"
              onClick={handleClear}
              style={{
                padding: "0.75rem 1.5rem",
                backgroundColor: "transparent",
                color: "#9ca3af",
                border: "1px solid #333",
                borderRadius: "6px",
                fontSize: "1rem",
                fontWeight: "600",
                cursor: "pointer",
              }}
            >
              Clear
            </button>
          )}
        </div>

        {error && (
          <div style={{ 
            marginTop: "1rem", 
            padding: "1rem", 
            backgroundColor: "#7f1d1d", 
            border: "1px solid #991b1b",
            borderRadius: "6px",
            color: "#fecaca"
          }}>
            <strong>Error:</strong> {error}
          </div>
        )}
      </form>

      <style jsx>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>

      {results && (
        <div id="results-section">
          <div style={{ 
            backgroundColor: "#1e293b", 
            padding: "1.5rem", 
            borderRadius: "8px", 
            marginBottom: "2rem" 
          }}>
            <h2 style={{ fontSize: "1.25rem", fontWeight: "600", marginBottom: "1rem" }}>
              Resume Analysis
            </h2>
            <div style={{ display: "grid", gap: "1rem" }}>
              <div>
                <strong>Skills:</strong>{" "}
                {results.resume_analysis.skills.join(", ") || "None detected"}
              </div>
              <div>
                <strong>Experience:</strong> {results.resume_analysis.years_experience} years
              </div>
              <div>
                <strong>Preferred Roles:</strong>{" "}
                {results.resume_analysis.preferred_roles.map(role => {
                  const lower = role.toLowerCase();
                  if (lower === 'ai') return 'AI';
                  return role.charAt(0).toUpperCase() + role.slice(1);
                }).join(", ") || "Not specified"}
              </div>
              <div>
                <strong>Seniority:</strong> {results.resume_analysis.seniority}
              </div>
            </div>
          </div>

          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem", flexWrap: "wrap", gap: "1rem" }}>
            <h2 style={{ fontSize: "1.5rem", fontWeight: "600", margin: 0 }}>
              Matched Jobs ({results.total_matches} total)
            </h2>
            <button
              onClick={handleClear}
              style={{
                padding: "0.5rem 1rem",
                backgroundColor: "#3b82f6",
                color: "white",
                border: "none",
                borderRadius: "6px",
                fontSize: "0.875rem",
                fontWeight: "600",
                cursor: "pointer",
              }}
            >
              Try Another Resume
            </button>
          </div>

          {results.matched_jobs.length === 0 ? (
            <p style={{ color: "#888" }}>No matching jobs found. Try updating your resume or check back later.</p>
          ) : (
            <div style={{ display: "grid", gap: "1.5rem" }}>
              {results.matched_jobs.map((job) => (
                <div
                  key={job.id}
                  style={{
                    backgroundColor: "#0f0f0f",
                    border: "1px solid #333",
                    borderRadius: "8px",
                    padding: "1.5rem",
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start", marginBottom: "1rem", flexWrap: "wrap", gap: "1rem" }}>
                    <div style={{ flex: 1, minWidth: "200px" }}>
                      <Link
                        href={`/job/${job.id}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{ 
                          fontSize: "1.25rem", 
                          fontWeight: "600", 
                          color: "#3b82f6",
                          textDecoration: "none"
                        }}
                      >
                        {job.title} →
                      </Link>
                      <p style={{ color: "#ccc", marginTop: "0.25rem" }}>{job.company}</p>
                    </div>
                    <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: "0.5rem" }}>
                      <div
                        style={{
                          backgroundColor: getMatchColor(job.match_percentage),
                          color: "white",
                          padding: "0.5rem 1rem",
                          borderRadius: "6px",
                          fontWeight: "600",
                          fontSize: "1.125rem",
                        }}
                      >
                        {job.match_percentage}% Match
                      </div>
                      <div style={{ width: "150px", height: "6px", backgroundColor: "#333", borderRadius: "3px", overflow: "hidden" }}>
                        <div style={{ 
                          width: `${job.match_percentage}%`, 
                          height: "100%", 
                          backgroundColor: getMatchColor(job.match_percentage),
                          transition: "width 0.5s ease-out"
                        }}></div>
                      </div>
                    </div>
                  </div>

                  <div style={{ marginBottom: "1rem" }}>
                    <p style={{ color: "#9ca3af", fontSize: "0.875rem" }}>
                      {job.match_explanation}
                    </p>
                  </div>

                  {job.matched_skills.length > 0 && (
                    <div style={{ marginBottom: "1rem" }}>
                      <strong style={{ fontSize: "0.875rem", color: "#9ca3af" }}>Matching Skills: </strong>
                      <span style={{ fontSize: "0.875rem" }}>
                        {job.matched_skills.join(", ")}
                      </span>
                    </div>
                  )}

                  <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", fontSize: "0.875rem" }}>
                    <span style={{ color: "#888" }}>📍 {job.location}</span>
                    {job.remote && <span style={{ color: "#6ee7b7" }}>🌐 Remote</span>}
                    {job.salary && <span style={{ color: "#10b981" }}>💰 {job.salary}</span>}
                    <span style={{ 
                      backgroundColor: "#1e3a8a", 
                      color: "#93c5fd",
                      padding: "0.25rem 0.75rem",
                      borderRadius: "4px"
                    }}>
                      {job.role}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      <footer className="jobs-footer">
        <div className="footer-content">
          <span>© 2026 maria c. lima</span>
          <span>|</span>
          <a 
            href="mailto:maria.lima.hub@gmail.com"
            className="footer-email"
          >
            <svg 
              fill="currentColor" 
              viewBox="0 0 24 24"
              className="footer-email-icon"
            >
              <path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/>
            </svg>
            <span>maria.lima.hub@gmail.com</span>
          </a>
        </div>
      </footer>
    </div>
  );
}
