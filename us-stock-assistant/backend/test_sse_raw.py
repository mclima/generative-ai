"""Test raw SSE connection"""
import asyncio
import httpx

async def test_sse():
    async with httpx.AsyncClient(timeout=None) as client:
        request = client.build_request(
            "GET",
            "http://localhost:8001/sse",
            headers={"Accept": "text/event-stream"}
        )
        response = await client.send(request, stream=True)
        
        print(f"Status: {response.status_code}")
        print("Reading SSE stream...")
        
        buffer = ""
        count = 0
        async for chunk in response.aiter_text():
            buffer += chunk
            print(f"Chunk {count}: {repr(chunk)}")
            count += 1
            if count > 5:  # Read first few chunks
                break
        
        print(f"\nFull buffer: {repr(buffer)}")

if __name__ == "__main__":
    asyncio.run(test_sse())
