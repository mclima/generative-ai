const res = await fetch(
  "https://your-api.up.railway.app/jobs?role=frontend&remote=true"
)
const jobs = await res.json()
console.log(jobs)