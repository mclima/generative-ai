import { getJobs } from "@/lib/api";
import JobCard from "@/components/JobCard";
import JobsClient from "@/components/JobsClient";
import Link from "next/link";

export default async function HomePage() {
  const jobs = await getJobs();

  return (
    <div className="jobs-container">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "2rem" }}>
        <h1 className="jobs-title" style={{ marginBottom: 0 }}>
          Agentic Tech Job Board
        </h1>
        <Link
          href="/match"
          style={{
            padding: "0.75rem 1.5rem",
            backgroundColor: "#3b82f6",
            color: "white",
            borderRadius: "6px",
            textDecoration: "none",
            fontWeight: "600",
            fontSize: "0.875rem",
          }}
        >
          🎯 Match Resume
        </Link>
      </div>

      <div className="features-section">
        <h3 className="features-title">
          Features
        </h3>
        <ul className="features-list">
          <li>✓ LangGraph multi-agent architecture</li>
          <li>✓ Parallel job ingestion from multiple sources</li>
          <li>✓ AI-powered resume matching with file upload</li>
          <li>✓ PostgreSQL persistence with deduplication</li>
          <li>✓ Next.js frontend with modern UI</li>
        </ul>
      </div>

      <JobsClient jobs={jobs} />

      {jobs.length === 0 && (
        <p className="no-jobs-message">
          No jobs found. Try refreshing the page.
        </p>
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
