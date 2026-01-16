"use client";

export default function ApplyButton({ url }: { url: string }) {
  return (
    <a
      href={url}
      target="_blank"
      rel="noopener noreferrer"
      className="apply-button"
    >
      Apply Now →
    </a>
  );
}
