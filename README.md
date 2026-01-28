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

To optimize deployments and only deploy apps when their specific folders have changes, use Railway's native GitHub integration with Watch Paths.

### Setup for Each Railway Service

For each service in your Railway project, configure the following:

1. **Connect GitHub Repository**
   - Open your Railway service (e.g., NewsGenie, Stock Agent Backend, etc.)
   - Go to **Settings → Source**
   - Click **Connect GitHub Repo**
   - Select your `generative-ai` repository
   - Choose the branch (e.g., `main`)

2. **Configure Watch Paths and Root Directory**
   - In the same service, go to **Settings → Build**
   - Set **Root Directory** to the service's folder path
   - Set **Watch Paths** to monitor only that service's directory
   
   **Example configurations:**
   
   | Service | Root Directory | Watch Paths |
   |---------|---------------|-------------|
   | NewsGenie | `newsgenie` | `newsgenie/**` |
   | Stock Agent Backend | `stock-agent/backend` | `stock-agent/backend/**` |
   | Tech Job Board Backend | `tech-job-board/backend` | `tech-job-board/backend/**` |
   | Research Assistant Backend | `research-assistant/backend` | `research-assistant/backend/**` |
   | Research Assistant Frontend | `research-assistant/frontend` | `research-assistant/frontend/**` |

3. **How It Works**
   - Railway will automatically deploy **only** when files in the specified Watch Paths change
   - Changes to other folders in the monorepo will **not** trigger deployments for that service
   - Each service deploys independently based on its own Watch Paths
   - No GitHub Actions or tokens needed - Railway handles everything automatically

### Benefits

- ✅ Automatic deployments when you push changes to specific directories
- ✅ No manual token management or GitHub Actions configuration
- ✅ Each service deploys independently
- ✅ Optimized build times - only affected services rebuild
- ✅ Native Railway integration with full deployment logs and rollback support


