"""
Utility functions for ULTRA DEEP RESEARCH.
"""

import asyncio
import time
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class SearchResult:
    """Data class for search results."""
    query: str
    content: str
    source: str
    timestamp: float
    relevance_score: float = 0.0

@dataclass
class ResearchStats:
    """Data class for research statistics."""
    total_queries: int = 0
    completed_searches: int = 0
    failed_searches: int = 0
    high_quality_results: int = 0
    processing_time: float = 0.0
    start_time: float = 0.0
    
    def start_timing(self):
        """Start timing the research process."""
        self.start_time = time.time()
    
    def end_timing(self):
        """End timing and calculate total processing time."""
        self.processing_time = time.time() - self.start_time
    
    def get_completion_rate(self) -> float:
        """Get the completion rate as a percentage."""
        if self.total_queries == 0:
            return 0.0
        return (self.completed_searches / self.total_queries) * 100
    
    def get_success_rate(self) -> float:
        """Get the success rate as a percentage."""
        total_attempts = self.completed_searches + self.failed_searches
        if total_attempts == 0:
            return 0.0
        return (self.completed_searches / total_attempts) * 100

async def rate_limit_delay(calls_made: int, rate_limit: int, delay_window: float = 60.0):
    """Implement rate limiting for API calls."""
    if calls_made >= rate_limit:
        sleep_time = delay_window - (time.time() % delay_window)
        await asyncio.sleep(sleep_time)
        return 0
    return calls_made + 1

def deduplicate_results(results: List[SearchResult]) -> List[SearchResult]:
    """Remove duplicate results based on content similarity."""
    seen_content = set()
    unique_results = []
    
    for result in results:
        # Simple deduplication based on content hash
        content_hash = hash(result.content[:200])  # First 200 chars
        if content_hash not in seen_content:
            seen_content.add(content_hash)
            unique_results.append(result)
    
    return unique_results

def rank_results(results: List[SearchResult]) -> List[SearchResult]:
    """Rank results by relevance and quality."""
    # Simple ranking based on content length and relevance score
    for result in results:
        # Boost score for longer, more detailed content
        length_bonus = min(len(result.content) / 1000, 1.0)  # Max 1.0 bonus
        result.relevance_score += length_bonus
    
    return sorted(results, key=lambda x: x.relevance_score, reverse=True)
