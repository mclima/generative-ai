# Tech Job Board - Frontend

Next.js frontend for the Tech Job Board application with responsive design and AI-powered resume matching.

## Features

- Browse remote tech jobs by category
- Sort jobs by date (newest/oldest)
- View detailed job descriptions
- AI-powered resume matching
- Responsive design (mobile, tablet, desktop)
- SEO-friendly
- Accessible (ARIA labels, keyboard navigation)
- Dark theme (black background, white text, blue accents)

## Tech Stack

- Next.js 14 (App Router)
- React 18
- TypeScript
- Tailwind CSS
- Axios for API calls
- Lucide React for icons
- date-fns for date formatting

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create `.env.local` file:
```bash
cp .env.local.example .env.local
```

3. Update the API URL in `.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. Run the development server:
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Build for Production

```bash
npm run build
npm start
```

## Deployment to Vercel

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Login to Vercel:
```bash
vercel login
```

3. Deploy:
```bash
vercel
```

4. Set environment variables in Vercel dashboard:
   - `NEXT_PUBLIC_API_URL` - Your Railway backend URL

## Project Structure

```
src/
├── app/                    # Next.js app router pages
│   ├── jobs/[id]/         # Job details page
│   ├── match-resume/      # Resume matching page
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Home page
│   └── globals.css        # Global styles
├── components/            # React components
│   ├── CategoryTabs.tsx
│   ├── Header.tsx
│   ├── JobCard.tsx
│   ├── MatchedJobCard.tsx
│   └── SortDropdown.tsx
├── lib/                   # Utilities
│   ├── api.ts            # API client
│   └── utils.ts          # Helper functions
└── types/                # TypeScript types
    └── index.ts
```

## Features

### Job Listings
- View all jobs or filter by category (AI, Engineering)
- Sort by newest or oldest
- Click job title to view details

### Job Details
- Full job description with HTML formatting
- Company, location, date posted, salary (if available)
- Category and source information
- Apply button with external link

### Resume Matching
- Upload resume (PDF, DOCX, TXT) or paste text
- AI-powered matching algorithm
- Match scores with color coding:
  - 🟢 Green (80-100%): Strong Match
  - 🟠 Orange (60-79%): Moderate Match
- Sorted by match score (highest first)
