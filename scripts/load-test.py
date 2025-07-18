import asyncio
import aiohttp
import time
import json
from typing import List

async def send_request(session: aiohttp.ClientSession, url: str, payload: dict) -> dict:
    """Send a single request to the API"""
    start_time = time.time()
    try:
        async with session.post(url, json=payload) as response:
            result = await response.json()
            end_time = time.time()
            return {
                'status': response.status,
                'response_time': end_time - start_time,
                'success': response.status == 200,
                'result': result
            }
    except Exception as e:
        end_time = time.time()
        return {
            'status': 0,
            'response_time': end_time - start_time,
            'success': False,
            'error': str(e)
        }

async def load_test(url: str, concurrent_requests: int = 10, total_requests: int = 100):
    """Run load test against the API"""
    
    payload = {
        "prompt": "Hello, how are you?",
        "max_length": 50,
        "temperature": 0.7
    }
    
    results = []
    
    async with aiohttp.ClientSession() as session:
        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(concurrent_requests)
        
        async def bounded_request():
            async with semaphore:
                return await send_request(session, url, payload)
        
        # Send all requests
        tasks = [bounded_request() for _ in range(total_requests)]
        results = await asyncio.gather(*tasks)
    
    # Analyze results
    successful_requests = [r for r in results if r['success']]
    failed_requests = [r for r in results if not r['success']]
    
    if successful_requests:
        avg_response_time = sum(r['response_time'] for r in successful_requests) / len(successful_requests)
        min_response_time = min(r['response_time'] for r in successful_requests)
        max_response_time = max(r['response_time'] for r in successful_requests)
    else:
        avg_response_time = min_response_time = max_response_time = 0
    
    print(f"Load Test Results:")
    print(f"Total Requests: {total_requests}")
    print(f"Successful Requests: {len(successful_requests)}")
    print(f"Failed Requests: {len(failed_requests)}")
    print(f"Success Rate: {len(successful_requests)/total_requests*100:.2f}%")
    print(f"Average Response Time: {avg_response_time:.2f}s")
    print(f"Min Response Time: {min_response_time:.2f}s")
    print(f"Max Response Time: {max_response_time:.2f}s")

if __name__ == "__main__":
    # Update with your actual endpoint
    api_url = "http://llm-api.your-domain.com/generate"
    asyncio.run(load_test(api_url, concurrent_requests=5, total_requests=50))
    