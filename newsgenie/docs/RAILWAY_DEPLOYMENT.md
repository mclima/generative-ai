# Railway Deployment Guide

## Quick Deployment Steps

1. **Push to GitHub** (if not already done)

2. **Railway Dashboard**:
   - Create new project
   - Connect GitHub repo: `generative-ai/newsgenie`
   - Railway auto-detects Python

3. **Environment Variables** (in Railway dashboard):
   ```
   OPENAI_API_KEY=sk-...
   GNEWS_API_KEY=...
   TAVILY_API_KEY=tvly-...
   PORT=8501
   ```

4. **Start Command** (in Railway settings):
   ```
   streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```

5. **Deploy**: Railway will build and deploy automatically

## Domain

Railway provides a public URL: `https://newsgenie-production.up.railway.app`

You can add a custom domain in settings.

## Notes

- Paid tier: No sleep, better resources
- Auto-deploys on git push
- Check logs in Railway dashboard for debugging
