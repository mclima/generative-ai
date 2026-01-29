Prompt: Build a Tech Job Board AI Application

You are an AI engineer responsible for designing and implementing a production-ready Tech Job Board application. Follow the requirements exactly and make reasonable engineering decisions where details are not explicitly specified.

1. Core Objective

Build an AI-powered web application that aggregates remote-only tech job listings in the United States, stores them in a database, and allows users to browse, filter, sort, and match jobs against their resumes.

2. Job Listings Requirements

Aggregate job listings from multiple job boards

Only include jobs:

Posted within the last 14 days

Remote-only

Located in US (Remote)

Display tech jobs only, limited to the following categories:

AI

Engineering

3. Job Categories & Navigation

Include an All Jobs tab

Include a separate tab for each category listed above

Job listings must appear under the correct category and in the All Jobs tab

4. Sorting Behavior

Allow users to sort job listings by date:

Newest First

Oldest First

Default sorting:

Newest First on initial load

Sorting applies to:

All Jobs

Each category tab

5. Database & Refresh Strategy

The application must include a database for job listings

Behavior:

Jobs are retrieved from the database on page load

Jobs are refreshed daily at 3am EST via scheduled cron job

Users can manually refresh jobs using the "Refresh Jobs" button

When fetching from job boards:

Compare incoming listings with existing database records

Add only new job listings to the database

Do not duplicate existing records

6. Job Listing UI

Display job listings in a card format

Each card must include:

Job title (clickable)

Company

Location

Date posted

Category

Source (job board)

7. Job Details Page

Clicking a job title navigates to a Job Details page

The Job Details page must display:

Job title

Full job description (use HTML to format the description)

Company

Location

Date posted

Salary (if available)

Category

Source

Apply button (external link or placeholder)

Include any additional relevant information that improves usability

8. Resume Matching Feature

The Jobs page must include a “Match Resume” button

Clicking the button navigates to a resume matching page where the user can:

Upload a resume (PDF, DOCX, TXT)

OR paste resume text

The system must:

Analyze the resume

Match it against stored job listings

Matching logic:

a. Skill overlap (40% weight) - Technical skills matching

b. Semantic similarity (35% weight) - Uses Sentence Transformers (all-MiniLM-L6-v2) with pre-computed embeddings
   - Job embeddings (3 per job: full, responsibilities, requirements) pre-computed during job refresh and cached in PostgreSQL
   - Resume embeddings (3 total: full, experience, skills) computed once per matching session
   - Weighted combination: 60% overall similarity + 40% section-specific similarities

c. Job title similarity (25% weight) - Role alignment

Minimum match threshold: 60% - Only jobs scoring 60% or higher are displayed

Performance: ~15-20 seconds for matching (including AI explanations for top matches)

AI Match Explanations:
- Generate personalized explanations for top 5 matches with score >= 80%
- Use OpenAI GPT-4o-mini to create 2-3 sentence insights
- Explain why the job is a strong fit
- Highlight aligned skills and relevant experience
- Identify growth opportunities
- Display with sparkle icon (✨) and gradient background
- Generated after matching completes (progress: 90-100%)

Implement a matching score algorithm (once you implement the matching logic formula (math + pseudocode), plase include it in a .md file)

Display matched jobs:

Sorted by matching score (highest first)

Each matched job card shows:
- AI Match Insight (for top 5 matches with 80%+ score)
- Individual component scores (semantic, skills, title)
- Matched skills from resume
- Score weights and calculations

Score display rules:

| Score Range | Meaning        | UI Color                             |
| ----------- | -------------- | ------------------------------------ |
| 80–100%     | Strong Match   | 🟢 Green                             |
| 60–79%      | Moderate Match | 🟠 Orange                            |


Each matched job must display in a card format:

Job title (clickable → Job Details page)

Company

Location

Date posted

Category

Source

Resume Page Info Box

Display the following message at the top of the resume matching page:

“Tip: For best results, use an ATS-compatible resume format (plain text, clear headings, standard fonts, no complex formatting or graphics).”

9. Backend Requirements

Use the following technologies:

Python

FastAPI

Sentence Transformers (all-MiniLM-L6-v2)

OpenAI GPT-4o-mini (for match explanations)

LangChain (for LLM integration)

scikit-learn (for cosine similarity)

PostgreSQL (with embedding storage in TEXT columns as JSON arrays)

Backend responsibilities:

Job ingestion & normalization

Database operations (PostgreSQL) with pre-computed embeddings

Resume parsing & matching logic with cached embeddings

API endpoints for frontend consumption

Secure handling of uploaded resumes

Background task processing for long-running operations

10. Frontend Requirements

Use React and Next.js

The frontend must be:

Accessible (ARIA, keyboard navigation)

Responsive (mobile, tablet, desktop)

SEO-friendly

UI Theme:

Black background

White text

Links and buttons in blue: #3b82f6

11. Deployment

Frontend:

Deploy to Vercel

Backend:

Deploy to Railway

12. Non-Functional Requirements

Application must be:

Scalable

Secure

Production-ready

Follow best practices for:

API design

Data validation

Error handling

Performance optimization

13. Expected Output

Clear backend and frontend architecture

Clean, readable, well-documented code

Reasonable assumptions explained in comments

No unnecessary complexity or overengineering

