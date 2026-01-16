"use client";

import Link from "next/link";

type Job = {
  id: string | number;
  title: string;
  company: string;
  location?: string;
  remote: boolean;
  role: string;
  source: string;
  url?: string;
  posted_date?: string;
};

export default function JobCard({ job, currentRole }: { job: Job; currentRole?: string | null }) {
  const jobLink = currentRole ? `/job/${job.id}?role=${currentRole}` : `/job/${job.id}`;
  
  return (
    <article
      role="article"
      aria-label={`Job posting: ${job.title} at ${job.company}`}
      className="job-card"
    >
      <h2 className="job-card-title">
        <Link 
          href={jobLink}
          aria-label={`View job details: ${job.title} at ${job.company}`}
          className="job-card-link"
        >
          {job.title} →
        </Link>
      </h2>
      
      <div className="job-card-content">
        <p className="job-card-company">
          <strong>{job.company}</strong>
        </p>
        <p className="job-card-location">
          📍 {job.location || "Remote"}
        </p>
        {job.posted_date && (() => {
          const date = new Date(job.posted_date);
          const isValidDate = !isNaN(date.getTime());
          return isValidDate ? (
            <p className="job-card-date">
              📅 {date.toLocaleDateString('en-US', { 
                year: 'numeric', 
                month: 'short', 
                day: 'numeric' 
              })}
            </p>
          ) : null;
        })()}
      </div>
      
      <div className="job-card-footer">
        <span 
          className="job-card-badge"
          aria-label={`Job category: ${job.role}`}
        >
          {job.role}
        </span>
        <span 
          className="job-card-source"
          aria-label={`Job source: ${job.source}`}
        >
          {job.source}
        </span>
      </div>
    </article>
  );
}
