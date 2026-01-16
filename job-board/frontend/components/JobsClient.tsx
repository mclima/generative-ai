"use client";

import { useState, useMemo, useEffect } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import JobCard from "./JobCard";
import JobFilter from "./JobFilter";

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

type JobsClientProps = {
  jobs: Job[];
};

export default function JobsClient({ jobs }: JobsClientProps) {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [selectedRole, setSelectedRole] = useState<string | null>(null);
  const [sortByDate, setSortByDate] = useState<"newest" | "oldest" | null>("newest");

  // Initialize from URL params
  useEffect(() => {
    const roleParam = searchParams.get('role');
    if (roleParam) {
      setSelectedRole(roleParam);
    }
  }, [searchParams]);

  // Update URL when role changes
  const handleRoleChange = (role: string | null) => {
    setSelectedRole(role);
    if (role) {
      router.push(`/?role=${role}`, { scroll: false });
    } else {
      router.push('/', { scroll: false });
    }
  };

  const filteredAndSortedJobs = useMemo(() => {
    let result = selectedRole 
      ? jobs.filter((job) => job.role === selectedRole)
      : jobs;

    if (sortByDate) {
      result = [...result].sort((a, b) => {
        const dateA = a.posted_date ? new Date(a.posted_date).getTime() : 0;
        const dateB = b.posted_date ? new Date(b.posted_date).getTime() : 0;
        return sortByDate === "newest" ? dateB - dateA : dateA - dateB;
      });
    }

    return result;
  }, [jobs, selectedRole, sortByDate]);

  return (
    <>
      <JobFilter onFilterChange={handleRoleChange} selectedRole={selectedRole} />

      <div className="jobs-header">
        <div className="jobs-count">
          Showing {filteredAndSortedJobs.length} of {jobs.length} jobs
          {selectedRole && (
            <span className="jobs-count-filter">
              • Filtered by: {selectedRole}
            </span>
          )}
        </div>

        <div className="jobs-sort-container">
          <span className="jobs-sort-label">Sort:</span>
          <button
            onClick={() => setSortByDate(sortByDate === "newest" ? null : "newest")}
            className={`sort-button ${sortByDate === "newest" ? "active" : ""}`}
          >
            Newest
          </button>
          <button
            onClick={() => setSortByDate(sortByDate === "oldest" ? null : "oldest")}
            className={`sort-button ${sortByDate === "oldest" ? "active" : ""}`}
          >
            Oldest
          </button>
        </div>
      </div>

      <section 
        aria-label="Job listings"
        className="jobs-grid"
      >
        {filteredAndSortedJobs.map((job: Job) => (
          <JobCard key={job.id} job={job} currentRole={selectedRole} />
        ))}
      </section>

      {filteredAndSortedJobs.length === 0 && (
        <p className="jobs-empty">
          No jobs found for this category. Try selecting a different filter.
        </p>
      )}
    </>
  );
}
