const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://generative-ai-production-621e.up.railway.app";

export async function getJobs() {
  const res = await fetch(
    `${API_URL}/jobs?limit=150`,
    {
      cache: "no-store",
    }
  );

  if (!res.ok) {
    throw new Error("Failed to fetch jobs");
  }

  return res.json();
}

export async function getJob(id: string | number) {
  const res = await fetch(
    `${API_URL}/jobs/${id}`,
    {
      cache: "no-store",
    }
  );

  if (!res.ok) {
    throw new Error("Failed to fetch job");
  }

  return res.json();
}

export async function getLLMConfig() {
  const res = await fetch(`${API_URL}/config/llm`);
  
  if (!res.ok) {
    throw new Error("Failed to fetch LLM config");
  }
  
  return res.json();
}
