"""
Search executor for handling async Perplexity API calls via OpenRouter.
"""

import asyncio
import httpx
import json
import time
from typing import List, Dict, Any
from rich.progress import Progress, TaskID
from rich.console import Console

from .utils import SearchResult, ResearchStats, rate_limit_delay
from config import config

console = Console()

class SearchExecutor:
    """Handles asynchronous search execution via OpenRouter API using AI models."""
    
    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(600.0, connect=15.0),  # 10 minutes total, 15s connect
            headers={
                "Authorization": f"Bearer {config.openrouter_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://utra-deep-research.com",
                "X-Title": "ULTRA DEEP RESEARCH"
            },
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        )
        self.calls_made = 0
        self.stats = ResearchStats()
    
    async def execute_search(self, query: str, search_num: int = None, total_searches: int = None) -> SearchResult:
        """Execute a single search query via Perplexity API."""
        try:
            # Show search start
            if search_num is not None and total_searches is not None:
                query_preview = query[:50] + "..." if len(query) > 50 else query
                console.print(f"[{search_num:2d}/{total_searches}] {query_preview}")
            
            # Implement rate limiting
            self.calls_made = await rate_limit_delay(
                self.calls_made, 
                config.api_rate_limit
            )
            
            # Prepare the request using the configured search model
            request_data = {
                "model": config.search_model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a research assistant. Provide comprehensive, factual information about the given topic based on your knowledge."
                    },
                    {
                        "role": "user",
                        "content": f"Provide comprehensive information about: {query}"
                    }
                ],
                
                "temperature": 0.1
            }
            
            # Make the API call
            try:
                response = await self.client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    json=request_data
                )
            except asyncio.TimeoutError:
                console.print(f"    ❌ Connection timeout")
                self.stats.failed_searches += 1
                return SearchResult(
                    query=query,
                    content="Search failed: Connection timeout",
                    source="Error",
                    timestamp=time.time(),
                    relevance_score=0.0
                )
            except Exception as e:
                console.print(f"    ❌ Error: {str(e)[:30]}...")
                self.stats.failed_searches += 1
                return SearchResult(
                    query=query,
                    content=f"Search failed: {str(e)}",
                    source="Error",
                    timestamp=time.time(),
                    relevance_score=0.0
                )
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                
                # Show result with character count
                if search_num is not None:
                    console.print(f"    ✅ {len(content)} characters")
                
                # Update stats
                self.stats.completed_searches += 1
                
                return SearchResult(
                    query=query,
                    content=content,
                    source=f"{config.search_model} via OpenRouter",
                    timestamp=time.time(),
                    relevance_score=0.5  # Default score, will be adjusted later
                )
            else:
                if search_num is not None:
                    console.print(f"    ❌ Failed: HTTP {response.status_code}")
                else:
                    console.print(f"❌ Search failed: HTTP {response.status_code}")
                
                self.stats.failed_searches += 1
                
                return SearchResult(
                    query=query,
                    content=f"Search failed: HTTP {response.status_code}",
                    source="Error",
                    timestamp=time.time(),
                    relevance_score=0.0
                )
                
        except Exception as e:
            if search_num is not None:
                console.print(f"    ❌ Failed: {str(e)[:30]}...")
            else:
                console.print(f"❌ Search failed: {str(e)}")
            
            self.stats.failed_searches += 1
            
            return SearchResult(
                query=query,
                content=f"Search failed: {str(e)}",
                source="Error",
                timestamp=time.time(),
                relevance_score=0.0
            )
    
    async def execute_batch_searches(self, queries: List[str]) -> List[SearchResult]:
        """Execute multiple searches concurrently with rate limiting."""
        console.print(f"Starting {len(queries)} searches with {config.max_concurrent_searches} concurrent workers...")
        self.stats.total_queries = len(queries)
        self.stats.start_timing()
        
        # Create semaphore to limit concurrent searches
        semaphore = asyncio.Semaphore(config.max_concurrent_searches)
        
        async def bounded_search(query: str, index: int):
            async with semaphore:
                return await self.execute_search(query, index + 1, len(queries))
        
        # Execute all searches concurrently
        console.print("Creating search tasks...")
        tasks = [bounded_search(query, i) for i, query in enumerate(queries)]
        console.print("Executing all searches...")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        console.print("All searches completed.")
        
        # Filter out exceptions and convert to proper results
        valid_results = []
        for result in results:
            if isinstance(result, SearchResult):
                valid_results.append(result)
            elif isinstance(result, Exception):
                console.print(f"❌ Search exception: {str(result)}")
                self.stats.failed_searches += 1
        
        self.stats.end_timing()
        return valid_results
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    def get_stats(self) -> ResearchStats:
        """Get current research statistics."""
        return self.stats
