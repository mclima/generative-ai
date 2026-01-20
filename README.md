# Generative AI Projects

This repository contains multiple AI-powered applications:

- **constitution-assistant** - Constitutional law assistant application
- **groq-chatbot** - Chatbot powered by Groq
- **image-generator** - AI image generation tool
- **job-board** - Job board application
- **research-assistant** - Research assistance tool
- **task-maestro** - Task management application

## Vercel Deployment Configuration

To optimize deployments and only build apps when their specific folders have changes, configure the following settings in Vercel:

### 1. Configure Ignored Build Step

Navigate to: **Settings → Git → Ignored Build Step**

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

## Getting Started

Each project has its own README with specific setup instructions. Navigate to the individual project directories for more details.
