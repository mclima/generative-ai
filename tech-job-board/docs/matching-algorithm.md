# Resume Matching Algorithm

## Overview

The resume matching algorithm uses a hybrid approach combining multiple techniques to calculate a match score between a candidate's resume and job listings. The algorithm uses **Sentence Transformers** (all-MiniLM-L6-v2) for enhanced semantic understanding, along with skill overlap and job title similarity to provide accurate matching results.

**Key Technology:** Transformer-based embeddings capture semantic meaning beyond simple keyword matching, understanding synonyms, context, and relationships between concepts.

## Algorithm Components

### 1. Resume Analysis

The system first analyzes the resume using:
- **Skill Extraction**: Pattern matching against common technical skills
- **Job Title Extraction**: Identifies previous roles and positions
- **Semantic Analysis**: Extracts key sections (experience, skills) for embedding generation

### 2. Matching Score Calculation

The final match score is calculated using a weighted formula:

```
Final Score = (Title Score × 0.25) + (Skill Score × 0.40) + (Semantic Score × 0.35)
```

**Weight Distribution:**
- Skill Overlap: 40%
- Semantic Similarity: 35% (using Sentence Transformers)
- Title Similarity: 25%

**Rationale:** Skills receive the highest weight because demonstrable technical skills are the strongest indicator of job fit for technical roles. Semantic similarity provides important contextual understanding, while title alignment confirms role-level match.

### 3. Component Calculations

#### A. Title Similarity Score (25% weight)

Compares resume job titles with the target job title.

**Algorithm:**
1. Extract all job titles from resume
2. Compare each resume title with job title
3. Scoring logic:
   - Exact substring match: 1.0 (100%)
   - 2+ common words: 0.8 (80%)
   - No titles found: 0.3 (30% baseline)
   - No match: 0.4 (40%)

**Pseudocode:**
```
function calculateTitleSimilarity(resumeTitles, jobTitle):
    if resumeTitles is empty:
        return 0.3
    
    jobTitleLower = lowercase(jobTitle)
    
    for each resumeTitle in resumeTitles:
        resumeTitleLower = lowercase(resumeTitle)
        
        // Check for substring match
        if resumeTitleLower in jobTitleLower OR jobTitleLower in resumeTitleLower:
            return 1.0
        
        // Check for word overlap
        resumeWords = split(resumeTitleLower)
        jobWords = split(jobTitleLower)
        commonWords = intersection(resumeWords, jobWords)
        
        if length(commonWords) >= 2:
            return 0.8
    
    return 0.4
```

#### B. Skill Overlap Score (40% weight)

Measures the overlap between resume skills and job requirements.

**Algorithm:**
1. Extract skills from resume using pattern matching
2. Search for each skill in job description
3. Calculate overlap ratio
4. Apply multiplier to boost score

**Scoring Logic:**
```
0 matches: 0.2
1-2 matches: 0.4
3-5 matches: 0.6
6-8 matches: 0.8
9+ matches: 1.0
```

**Pseudocode:**
```
function calculateSkillOverlap(resumeSkills, jobDescription):
    if resumeSkills is empty:
        return 0.3
    
    jobDescLower = lowercase(jobDescription)
    matchingSkills = 0
    
    for each skill in resumeSkills:
        if skill in jobDescLower:
            matchingSkills += 1
    
    // Score based on absolute number of matches
    if matchingSkills == 0: return 0.2
    if matchingSkills <= 2: return 0.4
    if matchingSkills <= 5: return 0.6
    if matchingSkills <= 8: return 0.8
    return 1.0
```

**Skill Categories:**
- Programming Languages: Python, JavaScript, TypeScript, Java, C++, Go, Rust, etc.
- Frameworks: React, Vue, Angular, Django, Flask, FastAPI, Node.js, etc.
- Databases: SQL, PostgreSQL, MySQL, MongoDB, Redis, Elasticsearch
- Cloud/DevOps: AWS, Azure, GCP, Docker, Kubernetes, Terraform
- ML/AI: TensorFlow, PyTorch, scikit-learn, Machine Learning, Deep Learning
- Other: Git, CI/CD, REST API, GraphQL, Microservices, Agile

#### C. Semantic Similarity Score (35% weight)

Uses **Sentence Transformers** (all-MiniLM-L6-v2) with **pre-computed job embeddings** for fast matching.

**Algorithm:**
1. **Job Embeddings (Pre-computed during job refresh):**
   - Full job description embedding
   - Responsibilities section embedding
   - Requirements section embedding
   - Stored in PostgreSQL for reuse

2. **Resume Embeddings (Computed once per matching session):**
   - Full resume text embedding
   - Experience section embedding
   - Skills section embedding

3. **Similarity Calculation:**
   - Overall similarity: Resume full text vs Job full description
   - Section similarities: Resume experience vs Job responsibilities, Resume skills vs Job requirements
   - Weighted combination: 60% overall + 40% section-specific
   - Return similarity score (0-1)

**How Sentence Transformers Work:**

Sentence Transformers convert text into dense vector representations (embeddings) that capture semantic meaning:

```
Resume Text → Transformer Model → [0.234, -0.123, 0.456, ...] (384 dimensions)
Job Description → Transformer Model → [0.221, -0.118, 0.449, ...] (384 dimensions)
```

**Key Advantages:**
- ✅ Understands synonyms (e.g., "React.js" = "React" = "ReactJS")
- ✅ Captures context and relationships
- ✅ Works across different writing styles
- ✅ Pre-trained on 1+ billion sentence pairs

**Mathematical Formula:**

Cosine Similarity:
```
Cosine Similarity = (A · B) / (||A|| × ||B||)

where:
A = Resume embedding vector (384 dimensions)
B = Job Description embedding vector (384 dimensions)
A · B = Dot product of vectors
||A|| = Magnitude of vector A
||B|| = Magnitude of vector B
```

**Pseudocode:**
```
function calculateSemanticSimilarity(resumeText, job):
    try:
        // Load model (lazy loading - only once)
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        // Check if job has pre-computed embeddings
        if not job.embedding_full:
            // Fallback: compute on-the-fly
            embeddings = model.encode([resumeText, job.description])
            return cosineSimilarity(embeddings[0], embeddings[1])
        
        // Compute resume embeddings once (cached for session)
        if not cached_resume_embeddings:
            resume_sections = extractSections(resumeText)
            cached_resume_embeddings = {
                'full': model.encode(resumeText),
                'experience': model.encode(resume_sections.experience),
                'skills': model.encode(resume_sections.skills)
            }
        
        // Load pre-computed job embeddings from database
        job_emb_full = loadEmbedding(job.embedding_full)
        job_emb_resp = loadEmbedding(job.embedding_responsibilities)
        job_emb_req = loadEmbedding(job.embedding_requirements)
        
        // Calculate similarities
        overall_sim = cosineSimilarity(cached_resume_embeddings.full, job_emb_full)
        resp_sim = cosineSimilarity(cached_resume_embeddings.experience, job_emb_resp)
        req_sim = cosineSimilarity(cached_resume_embeddings.skills, job_emb_req)
        
        // Weighted combination
        section_avg = (resp_sim + req_sim) / 2
        final_sim = (overall_sim * 0.6) + (section_avg * 0.4)
        
        return final_sim
    catch error:
        return 0.5  // Default fallback
```

**Model Details:**
- **Name:** all-MiniLM-L6-v2
- **Size:** ~80MB
- **Output:** 384-dimensional vectors
- **Speed:** ~0.01-0.05 seconds per text
- **Source:** Hugging Face Sentence Transformers library

**Performance Optimization:**
- **Job embeddings:** Pre-computed during job refresh (one-time cost)
- **Resume embeddings:** Computed once per matching session (3 embeddings total)
- **Matching speed:** ~10 seconds for 50 jobs (down from 3-5 minutes)
- **Embeddings stored:** PostgreSQL TEXT columns as JSON arrays
- **Cache location:** `~/.cache/huggingface` for model persistence

### 4. Score Interpretation

The final score (0-100%) is categorized as follows:

| Score Range | Match Level    | UI Indicator | Meaning |
|-------------|----------------|--------------|---------|
| 80-100%     | Strong Match   | 🟢 Green     | Excellent fit, highly recommended |
| 60-79%      | Moderate Match | 🟠 Orange    | Good fit, worth considering |
| 0-59%       | Weak Match     | Not shown    | Not displayed to user |

**Note:** Only jobs with scores ≥ 60% are shown to users.

## Example Calculation

**Given:**
- Resume has titles: ["Senior Software Engineer", "Full Stack Developer"]
- Resume skills: ["Python", "React", "PostgreSQL", "AWS", "Docker"]
- Job title: "Senior Full Stack Engineer"
- Job description mentions: "Python, React, Node.js, AWS, Kubernetes"

**Calculation:**

1. **Title Score:**
   - "Senior Software Engineer" vs "Senior Full Stack Engineer"
   - Common words: "Senior", "Engineer" (2 words)
   - Score: 0.8

2. **Skill Score:**
   - Matching skills: Python, React, AWS (3 matches)
   - Score: 0.6 (3-5 matches range)

3. **Semantic Score:**
   - Sentence Transformer cosine similarity: 0.82 (example)

4. **Final Score:**
   ```
   Final = (0.8 × 0.25) + (0.6 × 0.40) + (0.82 × 0.35)
   Final = 0.20 + 0.24 + 0.287
   Final = 0.727 = 73%
   ```

**Result:** Moderate Match (🟠 Orange)

## Implementation Notes

- The algorithm is implemented in `backend/app/resume_matcher.py`
- Uses **Sentence Transformers** library with all-MiniLM-L6-v2 model
- Model is lazy-loaded (only loads once, shared across requests)
- **Pre-computed embeddings:** Job embeddings calculated during job refresh and stored in PostgreSQL
- **Embedding storage:** 3 TEXT columns per job (embedding_full, embedding_responsibilities, embedding_requirements)
- **Resume embeddings:** Computed once per matching session and cached in memory
- All scores are normalized to 0-1 range before final calculation
- Final score is multiplied by 100 and capped at 100%
- **Minimum match threshold: 60%** - Only jobs scoring 60% or higher are returned
- **Performance:** ~10 seconds for matching (3 resume embeddings vs 126+ in naive approach)
- Memory efficient: ~400-500MB total (model + runtime)
- Compatible with Railway deployment
- Word boundary matching for short skills (e.g., "golang", "rust", "java") to avoid false positives

## AI Match Explanations (Implemented)

For top 5 matches with scores ≥ 80%, the system generates personalized explanations using OpenAI GPT-4o-mini:

**Implementation:**
- Triggered after matching completes (progress: 90-100%)
- Concise 2-3 sentence explanations
- Focuses on: aligned skills, relevant experience, growth opportunities
- Adds `match_explanation` field to qualifying job results
- Graceful error handling (sets to None if generation fails)

**Prompt Strategy:**
```
Explain why this job is a strong match for the candidate in 2-3 sentences.

Job: {title} at {company}
Match Score: {score}%
Matched Skills: {top 10 skills}
Candidate Background: {job titles}

Focus on: aligned skills, relevant experience, and growth opportunities.
```

**Performance:**
- ~1-2 seconds per explanation
- Total: ~5-10 seconds for 5 explanations
- Overall matching time: ~15-20 seconds (including explanations)

## Future Improvements

Potential enhancements to the algorithm:
1. Add experience level matching (junior, mid, senior)
2. Include education requirements matching
3. Consider location preferences (if applicable)
4. Add industry/domain experience matching
5. Fine-tune the Sentence Transformer model on job-resume pairs
6. Add user feedback loop to improve matching accuracy
7. Implement vector database (ChromaDB, Pinecone) for 1000+ jobs scale
