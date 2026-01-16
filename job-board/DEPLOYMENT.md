# Deployment Guide

## Frontend - Vercel

### 1. Deploy to Vercel
1. Go to [vercel.com](https://vercel.com) and sign in
2. Click "Add New Project"
3. Import your GitHub repository
4. Select the `frontend` folder as the root directory
5. Framework Preset: **Next.js**
6. Build Command: `npm run build`
7. Output Directory: `.next`

### 2. Environment Variables
Add these in Vercel dashboard under Settings → Environment Variables:

```
NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
```

### 3. Deploy
Click "Deploy" and Vercel will build and deploy your frontend.

---

## Backend - Railway

### 1. Deploy to Railway
1. Go to [railway.app](https://railway.app) and sign in
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository (generative-ai)
5. **Important:** After the project is created, configure the root directory:
   - Click on your service in the Railway dashboard
   - Go to **Settings** tab
   - Scroll to **Root Directory**
   - Set it to: `backend`
   - Click **Save**
6. Go to **Deployments** tab and click **Redeploy** to rebuild with correct directory

### 2. Add PostgreSQL Database
1. In your Railway project, click "New"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically create a database and set `DATABASE_URL`

### 3. Environment Variables
Add these in Railway dashboard under Variables:

```
DATABASE_URL=${{Postgres.DATABASE_URL}}
OPENAI_API_KEY=your-openai-api-key
RAPIDAPI_KEY=your-rapidapi-key
ADZUNA_APP_ID=your-adzuna-app-id
ADZUNA_APP_KEY=your-adzuna-app-key
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.3
```

### 4. Configure Start Command
Railway should auto-detect the start command, but if needed, set it to:
```
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### 5. Deploy
Railway will automatically deploy when you push to your repository.

---

## Post-Deployment

### Update Frontend API URL
After deploying the backend, update the frontend environment variable:
1. Go to Vercel dashboard
2. Settings → Environment Variables
3. Update `NEXT_PUBLIC_API_URL` to your Railway backend URL
4. Redeploy the frontend

### Test the Deployment
1. Visit your Vercel frontend URL
2. Check that jobs are loading
3. Test the resume matcher
4. Verify API endpoints at `https://your-backend-url.railway.app/docs`

---

## Troubleshooting

### Backend Issues
- Check Railway logs for errors
- Verify all environment variables are set
- Ensure PostgreSQL database is connected
- Check that `DATABASE_URL` is properly formatted

### Frontend Issues
- Verify `NEXT_PUBLIC_API_URL` points to Railway backend
- Check browser console for CORS errors
- Ensure backend allows frontend origin in CORS settings

### Database Issues
- Railway PostgreSQL should auto-configure
- If needed, manually set: `postgresql://user:password@host:port/database`
- Run migrations if tables don't exist (they auto-create on first run)

---

## API Keys Required

**Required:**
- `OPENAI_API_KEY` - For resume matching and LLM features

**Optional (for job sources):**
- `RAPIDAPI_KEY` - For JSearch API
- `ADZUNA_APP_ID` + `ADZUNA_APP_KEY` - For Adzuna API

**Note:** The app will work with just OpenAI API key, but job ingestion will be limited to Jobicy only.
