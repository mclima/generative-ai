# Generative AI Projects

This repository contains multiple AI-powered applications:

- **constitution-assistant** - Constitutional law assistant application
- **groq-chatbot** - Chatbot powered by Groq
- **image-generator** - AI image generation tool
- **research-assistant** - Research assistance tool
- **stock-agent** - AI-powered stock analysis dashboard
- **tech-job-board** - AI-powered job board
- **task-maestro** - Task management application

## Vercel Deployment Configuration

To optimize deployments and only build apps when their specific folders have changes, configure the following settings in Vercel:

### 1. Configure Ignored Build Step

Navigate to: **Settings → Build and Deployment → Ignored Build Step**

- Select: **Only build if there are changes in a folder**
- Set the command to:
  ```bash
  git diff HEAD^ HEAD --quiet -- .
  ```

This command checks if there are changes in the current root directory. If no changes are detected, the build is skipped.

### 2. Configure Build and Deployment Settings

Navigate to: **Settings → Build and Deployment → Root Directory**

- **Disable**: "Include files outside the root directory in the Build Step"
- **Enable**: "Skip deployments when there are no changes to the root directory or its dependencies"

These settings ensure that:
- Each app only rebuilds when files in its specific directory change
- Changes to other apps in the monorepo won't trigger unnecessary deployments
- Build times and deployment costs are optimized

### 3. Custom Domain Setup (Spaceship)

To add a custom subdomain for your Vercel-deployed apps:

#### In Spaceship (DNS Provider)

1. Log in to your Spaceship account
2. Navigate to **Domains** → Select your domain → **DNS Settings**
3. Click **Add Record**
4. Configure the CNAME record:
   - **Type**: CNAME
   - **Name/Host**: Your subdomain (e.g., `stock-agent`, `chatbot`, `tasks`)
   - **Value/Points to**: `cname.vercel-dns.com`
   - **TTL**: Auto or 3600 (1 hour)
5. Click **Save**

#### In Vercel

1. Go to your project → **Settings** → **Domains**
2. Click **Add Domain**
3. Enter your full subdomain (e.g., `stock-agent.yourdomain.com`)
4. Click **Add**
5. If you see **"DNS Change Recommended"**, click it to get the exact CNAME value
6. Use the value provided by Vercel (usually `cname.vercel-dns.com` or a project-specific value)
7. Update your Spaceship CNAME record with this value if different
8. Wait 5-30 minutes for DNS propagation
9. SSL certificate will be automatically provisioned

**Example subdomains:**
- `stock-agent.yourdomain.com` → Stock Agent app
- `chatbot.yourdomain.com` → Groq Chatbot
- `tasks.yourdomain.com` → Task Maestro

## Getting Started

Each project has its own README with specific setup instructions. Navigate to the individual project directories for more details.

## Railway Deployment Configuration

To optimize deployments and only deploy apps when their specific folders have changes, configure the following settings in Railway:

### 1. Add GitHub Actions secret

In GitHub: **Settings → Secrets and variables → Actions → New repository secret**

- **Name**: `RAILWAY_TOKEN`
- **Value**: Railway **Project Token** for this Railway project

This token is used by the GitHub Actions workflow to run `railway up`.

### 2. Disconnect Railway auto-deploys from GitHub (per service)

Railway will deploy on any push to the connected branch by default. To ensure deploys only happen via GitHub Actions, disconnect GitHub as the source **for each Railway service**.

For each service (e.g. `tech-job-board-backend`, `research-assistant-backend`, etc.):

1. Open the service in Railway
2. Go to **Settings → Source**
3. Disconnect:
   - **Branch connected to production** (e.g. `main`)
   - **Source Repo** (e.g. `mclima/generative-ai`)
4. Click **Details → Deploy Changes** to apply the disconnect

Recommendation: **Disconnect both the branch and the repo**. Disconnecting only the branch may still leave the repo connected and can continue to trigger deployments.

### 3. Deploy via GitHub Actions (path-filtered)

This repo uses a path-filtered workflow: `.github/workflows/railway-deploy.yml`.

Deploys only run when changes occur under specific folders:

- `tech-job-board/backend/**` → deploy `tech-job-board-backend`
- `research-assistant/backend/**` → deploy `research-assistant-backend`
- `research-assistant/frontend/**` → deploy `research-assistant-frontend`
- `stock-agent/backend/**` → deploy `stock-agent-backend`
- `newsgenie/**` → deploy `NewsGenie`

Notes:

- Changes to `README.md` at the repo root will **not** trigger a Railway deployment.
- You can also manually run the workflow in GitHub Actions using **workflow_dispatch**.


