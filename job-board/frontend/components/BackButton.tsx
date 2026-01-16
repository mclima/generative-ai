"use client";

import { useRouter } from "next/navigation";

export default function BackButton({ role }: { role?: string }) {
  const router = useRouter();

  const handleBack = () => {
    if (role) {
      router.push(`/?role=${role}`);
    } else {
      router.push("/");
    }
  };

  return (
    <button
      onClick={handleBack}
      className="back-button"
    >
      ← Back to Jobs
    </button>
  );
}
