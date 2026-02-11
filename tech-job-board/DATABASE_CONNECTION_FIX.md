# Database Connection Timeout Fix

## Problem
The cron job at 3pm EST failed with HTTP 500 errors. Railway logs showed:
```
psycopg2.OperationalError: connection to server at "postgres.railway.internal" failed: Connection timed out
```

This caused the frontend to show only a loading gif with no jobs displayed.

## Root Causes
1. **No connection timeout configured** - psycopg2 defaulted to indefinite wait
2. **No retry logic** - Single connection failure caused immediate 500 error
3. **No connection validation** - Stale connections from the pool weren't detected
4. **Blocking init_db** - App failed to start if database was temporarily unavailable
5. **Poor error messaging** - Frontend didn't distinguish between error types
6. **Refresh button failure** - When database was down, refresh API failed and prevented fetching cached jobs

## Fixes Implemented

### 1. Database Connection Resilience (`backend/app/database.py`)
- **Connection timeout**: Set to 10 seconds
- **TCP keepalives**: Configured to detect dead connections
  - `keepalives=1`
  - `keepalives_idle=30`
  - `keepalives_interval=10`
  - `keepalives_count=5`
- **Retry logic**: 3 attempts with exponential backoff (1s, 2s, 3s)
- **Connection validation**: Test each connection with `SELECT 1` before use
- **Stale connection cleanup**: Close and discard failed connections

### 2. API Error Handling (`backend/app/main.py`)
- Wrapped critical endpoints in try-catch blocks
- Return HTTP 503 (Service Unavailable) for database errors instead of 500
- Added specific error messages for database unavailability
- Non-blocking `init_db()` - app starts even if database is temporarily down

### 3. **In-Memory Cache Fallback** (NEW)
- **Automatic caching**: Jobs are cached in memory on every successful database fetch
- **Graceful degradation**: When database is unavailable, returns cached jobs instead of error
- **Cache indicators**: 
  - Response header `X-Data-Source: cache` indicates cached data
  - Response header `X-Cache-Time` shows when cache was last updated
- **Frontend warning banner**: Orange alert shows when viewing cached jobs with timestamp
- **No more loading gif**: Users see old jobs instead of infinite loading when database is down

### 4. Health Check Endpoint
- New `/health` endpoint for monitoring
- Returns database connection status
- Can be used by Railway health checks or external monitoring

### 5. Frontend Error Handling (`frontend/src/app/HomePageClient.tsx`)
- Distinguish between 503 (database unavailable) and other errors
- Show user-friendly messages for temporary database issues
- **Cache detection**: Detects `X-Data-Source` header and displays warning banner
- **Visual feedback**: Orange banner with cache timestamp when showing cached jobs
- **Refresh button resilience**: Always attempts to fetch jobs (which returns cache) even if refresh API fails
  - Prevents "loading gif forever" when clicking refresh during database outage
  - Shows cached jobs with appropriate error message
- Improved error recovery with retry button

## Testing Recommendations

### 1. Test the Health Check
```bash
curl https://your-app.railway.app/health
```

### 2. Monitor Logs
Check Railway logs for:
- `Database initialized successfully` (on startup)
- `Database connection attempt X/3 failed` (during retries)
- `Database connection error in [endpoint]` (when retries exhausted)

### 3. Update GitHub Actions (Optional)
Add health check before running cron job:
```yaml
- name: Check API Health
  run: |
    curl -f https://your-app.railway.app/health || exit 1
    
- name: Refresh Jobs
  run: |
    curl -sS -f -X POST "https://your-app.railway.app/api/jobs/refresh"
```

## Railway Configuration Recommendations

### 1. Add Health Check
In Railway dashboard:
- Set health check path: `/health`
- This will help Railway detect when the app is ready

### 2. Database Connection Limits
Verify your PostgreSQL plan supports the connection pool size (currently 10 max connections)

### 3. Restart Policy
Current setting is good:
- `restartPolicyType: ON_FAILURE`
- `restartPolicyMaxRetries: 10`

## Expected Behavior Now

### When Database is Temporarily Unavailable:
1. **First request**: Retries 3 times over ~6 seconds
2. **If all retries fail AND cache exists**: 
   - Returns cached jobs with `X-Data-Source: cache` header
   - Frontend shows orange warning banner: "Database temporarily unavailable - showing cached jobs from X minutes ago"
   - Users can still browse jobs (better UX than loading gif)
3. **If all retries fail AND no cache**: Returns HTTP 503 with error message
4. **Next request**: Tries database again (connection may have recovered)

### When Database is Available:
- Connections succeed on first attempt
- Jobs are fetched and cache is updated automatically
- Keepalives maintain healthy connections
- Stale connections are detected and replaced
- No warning banner shown

## Monitoring

Watch for these patterns in Railway logs:
- **Good**: `Database initialized successfully`
- **Warning**: `Database connection attempt 2/3 failed` (retrying)
- **Error**: `Failed to connect to database after 3 attempts` (needs investigation)

## Next Steps

1. **Deploy these changes** to Railway
2. **Monitor the next cron job** at 3pm EST
3. **Check the `/health` endpoint** periodically
4. **Review Railway database metrics** for connection issues

If timeouts persist after these fixes, investigate:
- Railway database instance health
- Network connectivity between services
- Database connection limits/quotas
