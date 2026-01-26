export interface Job {
  id: number
  job_id: string
  title: string
  company: string
  location: string
  description: string
  category: string
  source: string
  posted_date: string
  salary: string | null
  apply_url: string
  created_at: string
}

export interface MatchedJob extends Job {
  match_score: number
  match_level: string
  matched_skills: string[]
  missed_skills: string[]
  title_score: number
  skill_score: number
  semantic_score: number
}
