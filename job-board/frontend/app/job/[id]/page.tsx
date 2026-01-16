import { getJob } from "@/lib/api";
import ApplyButton from "@/components/ApplyButton";
import BackButton from "@/components/BackButton";

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
  score?: number;
  description?: string;
  salary?: string;
  requirements?: string[];
  responsibilities?: string[];
};

export default async function JobDetailPage({ 
  params,
  searchParams 
}: { 
  params: { id: string };
  searchParams: { role?: string };
}) {
  const job: Job = await getJob(params.id);

  const formatDate = (dateString?: string) => {
    if (!dateString) return "Not specified";
    const date = new Date(dateString);
    const isValidDate = !isNaN(date.getTime());
    return isValidDate
      ? date.toLocaleDateString("en-US", {
          year: "numeric",
          month: "long",
          day: "numeric",
        })
      : "Not specified";
  };

  return (
    <div className="job-detail-container">
      <BackButton role={searchParams.role} />

      <article className="job-detail-article">
        <header className="job-detail-header">
          <h1 className="job-detail-title">
            {job.title}
          </h1>
          <div className="job-detail-meta">
            <span className="job-detail-company">{job.company}</span>
            <span className="job-detail-badge">
              {job.role}
            </span>
            {job.remote && (
              <span className="job-detail-badge-remote">
                Remote
              </span>
            )}
          </div>
        </header>

        <div className="job-detail-content">
          {job.requirements && job.requirements.length > 0 && (
            <section>
              <h2 className="job-detail-section-title">
                Requirements
              </h2>
              <ul className="job-detail-list">
                {job.requirements.map((req, idx) => (
                  <li key={idx} className="job-detail-list-item">
                    <span className="job-detail-list-icon-check">✓</span>
                    <span>{req}</span>
                  </li>
                ))}
              </ul>
            </section>
          )}

          {job.responsibilities && job.responsibilities.length > 0 && (
            <section>
              <h2 className="job-detail-section-title">
                Responsibilities
              </h2>
              <ul className="job-detail-list">
                {job.responsibilities.map((resp, idx) => (
                  <li key={idx} className="job-detail-list-item">
                    <span className="job-detail-list-icon-bullet">•</span>
                    <span>{resp}</span>
                  </li>
                ))}
              </ul>
            </section>
          )}

          {job.description && (
            <section>
              <h2 className="job-detail-section-title">
                Full Job Description
              </h2>
              <div className="job-detail-description">
                {job.description}
              </div>
            </section>
          )}

          {job.salary && (
            <section>
              <h2 className="job-detail-section-title">
                Salary
              </h2>
              <p className="job-detail-salary">💰 {job.salary}</p>
            </section>
          )}

          <section>
            <h2 className="job-detail-section-title">
              Location
            </h2>
            <p className="job-detail-info">📍 {job.location || "Remote"}</p>
          </section>

          <section>
            <h2 className="job-detail-section-title">
              Posted Date
            </h2>
            <p className="job-detail-info">📅 {formatDate(job.posted_date)}</p>
          </section>

          <section>
            <h2 className="job-detail-section-title">
              Source
            </h2>
            <p className="job-detail-info">{job.source}</p>
          </section>

          {job.score !== undefined && (
            <section>
              <h2 className="job-detail-section-title">
                Relevance Score
              </h2>
              <p className="job-detail-info">{job.score.toFixed(2)}</p>
            </section>
          )}

          {job.url && (job.url.startsWith("http://") || job.url.startsWith("https://")) && (
            <section className="job-detail-apply-section">
              <ApplyButton url={job.url} />
            </section>
          )}
        </div>

        <footer className="job-detail-footer">
          <p>Job ID: {job.id}</p>
        </footer>
      </article>
    </div>
  );
}
