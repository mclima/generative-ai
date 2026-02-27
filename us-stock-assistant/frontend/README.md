# US Stock Assistant Frontend

Next.js frontend for the US Stock Assistant application built with Next.js 14+ with App Router, React 18, TypeScript, and Tailwind CSS.

## Project Structure

```
frontend/
├── app/
│   ├── (auth)/              # Authentication pages (login, register)
│   ├── (dashboard)/         # Protected dashboard pages
│   ├── components/          # Reusable components (Header, Sidebar, Footer, ProtectedRoute)
│   ├── contexts/            # React contexts (AuthContext)
│   ├── lib/                 # Utilities and API clients
│   │   ├── api/             # API client modules (analysis, news, market, portfolio, stocks, alerts)
│   │   └── api-client.ts    # Axios instance with interceptors
│   └── types/               # TypeScript type definitions
```

## Features Implemented

### 1. Next.js Project Structure

- ✅ App Router directory structure with route groups
- ✅ Tailwind CSS configuration
- ✅ Layout components (Header, Sidebar, Footer)
- ✅ Environment variables for API URL
- ✅ Responsive design with mobile support

### 2. Authentication Context and Hooks

- ✅ AuthContext for managing user state
- ✅ useAuth hook for accessing auth state
- ✅ Login, logout, and register functions
- ✅ Token refresh logic (auto-refresh every 14 minutes)
- ✅ ProtectedRoute wrapper component

### 3. API Client Utilities

- ✅ Axios instance with interceptors for auth tokens
- ✅ API client functions for all backend endpoints
- ✅ Error handling and retry logic
- ✅ TypeScript types for all API requests/responses

## Setup

1. Install dependencies:

```bash
npm install
```

2. Copy environment file:

```bash
cp .env.local.example .env.local
```

3. Start the development server:

```bash
npm run dev
```

The application will be available at http://localhost:3000

## Build

Build for production:

```bash
npm run build
```

Start production server:

```bash
npm start
```

## Environment Variables

- `NEXT_PUBLIC_API_URL`: Backend API URL (default: http://localhost:8000)
