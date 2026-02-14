# Manual Testing Guide for Error Handling

## Quick Tests to Validate Error Handling

### Test 1: Invalid API Key (Search Failure)
1. Edit `.env` - change `TAVILY_API_KEY` to `invalid_key`
2. Restart backend: `export $(cat .env | xargs) && uvicorn main:app --host 0.0.0.0 --port 8000`
3. Submit a research query in the frontend
4. **Expected**: Should see fallback response with helpful links after 3 retry attempts

### Test 2: Invalid OpenAI Key (Writer Failure)  
1. Edit `.env` - change `OPENAI_API_KEY` to `invalid_key`
2. Restart backend
3. Submit a research query
4. **Expected**: Search/scrape may work, but writer fails → fallback response

### Test 3: Obscure Topic (Empty Results)
1. Use valid API keys
2. Search for: `xyzabc999nonexistent12345topic`
3. **Expected**: Invalid topic rejected with helpful message

### Test 4: Network Simulation
1. Disconnect internet briefly
2. Submit query
3. Reconnect
4. **Expected**: Retries should handle transient failures

