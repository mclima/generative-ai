# Tech Job Board - Setup Guide

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+

## Database Setup

### Option 1: PostgreSQL with Homebrew (macOS)

```bash
# Install PostgreSQL
brew install postgresql@14

# Start PostgreSQL service
brew services start postgresql@14

# Create database user
psql postgres -c "CREATE USER techjobuser WITH PASSWORD 'techjobpass';"

# Create database
psql postgres -c "CREATE DATABASE techjobboard OWNER techjobuser;"

# Grant privileges
psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE techjobboard TO techjobuser;"
psql techjobboard -c "GRANT ALL ON SCHEMA public TO techjobuser;"
```

### Option 2: PostgreSQL with Docker

```bash
docker run --name techjob-postgres \
  -e POSTGRES_USER=techjobuser \
  -e POSTGRES_PASSWORD=techjobpass \
  -e POSTGRES_DB=techjobboard \
  -p 5432:5432 \
  -d postgres:14
```

## Backend Setup

```bash
# Navigate to backend folder
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env file with your credentials
# OPENAI_API_KEY=your_openai_api_key
# DATABASE_URL=postgresql://techjobuser:techjobpass@localhost:5432/techjobboard
# ENVIRONMENT=development

# Run the backend server
uvicorn app.main:app --reload
```

Backend will be available at `http://localhost:8000`

## Frontend Setup

```bash
# Navigate to frontend folder
cd frontend

# Install dependencies
npm install

# Create .env.local file
cp .env.local.example .env.local

# Edit .env.local file
# NEXT_PUBLIC_API_URL=http://localhost:8000

# Run the development server
npm run dev
```

Frontend will be available at `http://localhost:3000`

## Verify Setup

- Backend API docs: `http://localhost:8000/docs`
- Frontend app: `http://localhost:3000`
- Database tables are created automatically on first backend startup
