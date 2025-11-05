"""
Result aggregator for processing and ranking search results.
"""

import re
from typing import List, Dict, Any, Tuple
from collections import Counter
from rich.console import Console

from .utils import SearchResult, ResearchStats, deduplicate_results, rank_results

console = Console()

class ResultAggregator:
    """Aggregates and processes search results to extract high-signal information."""
    
    def __init__(self):
        self.stats = ResearchStats()
    
    def aggregate_results(self, results: List[SearchResult]) -> Tuple[List[SearchResult], Dict[str, Any]]:
        """Aggregate and process search results."""
        console.print("📊 Aggregating and processing search results...")
        
        # Update stats
        self.stats.total_queries = len(results)
        self.stats.completed_searches = len([r for r in results if r.source != "Error"])
        self.stats.failed_searches = len([r for r in results if r.source == "Error"])
        
        # Step 1: Remove duplicates
        console.print("   • Removing duplicates...")
        unique_results = deduplicate_results(results)
        
        # Step 2: Filter out low-quality results
        console.print("   • Filtering low-quality content...")
        filtered_results = self._filter_quality(unique_results)
        
        # Step 3: Rank results by relevance
        console.print("   • Ranking by relevance...")
        ranked_results = rank_results(filtered_results)
        
        # Step 4: Extract key insights and themes
        console.print("   • Extracting key themes...")
        themes = self._extract_themes(ranked_results)
        
        # Step 5: Generate statistics
        console.print("   • Generating statistics...")
        statistics = self._generate_statistics(ranked_results, themes)
        
        # Update high-quality results count
        self.stats.high_quality_results = len(ranked_results)
        
        console.print(f"✅ Aggregation complete: {len(ranked_results)} high-quality results")
        return ranked_results, statistics
    
    def _filter_quality(self, results: List[SearchResult]) -> List[SearchResult]:
        """Filter out low-quality results based on content analysis."""
        filtered = []
        
        for result in results:
            content = result.content.lower()
            
            # Skip error results
            if result.source == "Error":
                continue
            
            # Skip very short content
            if len(content) < 100:
                continue
            
            # Skip content that seems to be error messages
            error_indicators = [
                "search failed", "error", "not found", "unable to", 
                "cannot", "failed", "timeout", "exception"
            ]
            
            if any(indicator in content for indicator in error_indicators):
                continue
            
            # Skip repetitive content
            if self._is_repetitive(content):
                continue
            
            # Boost score for substantive content
            if self._is_substantive(content):
                result.relevance_score += 0.3
            
            filtered.append(result)
        
        return filtered
    
    def _is_repetitive(self, content: str) -> bool:
        """Check if content is overly repetitive."""
        words = content.split()
        if len(words) < 20:
            return False
        
        # Check for repeated words or phrases
        word_counts = Counter(words)
        most_common_count = word_counts.most_common(1)[0][1]
        
        # If any word appears more than 30% of the time, it's repetitive
        if most_common_count / len(words) > 0.3:
            return True
        
        return False
    
    def _is_substantive(self, content: str) -> bool:
        """Check if content appears substantive and valuable."""
        substantive_indicators = [
            "research", "study", "analysis", "data", "evidence",
            "according to", "research shows", "study found",
            "experts believe", "results indicate", "conclusion",
            "methodology", "findings", "investigation"
        ]
        
        # Check for substantive keywords
        substantive_count = sum(1 for indicator in substantive_indicators if indicator in content.lower())
        
        # Check for length (longer content tends to be more substantive)
        length_score = min(len(content) / 1000, 1.0)
        
        # Combine factors
        substantive_score = (substantive_count * 0.1) + (length_score * 0.5)
        
        return substantive_score > 0.3
    
    def _extract_themes(self, results: List[SearchResult]) -> Dict[str, int]:
        """Extract common themes from search results."""
        all_content = " ".join([result.content for result in results[:20]])  # Top 20 results
        
        # Simple keyword extraction (could be enhanced with NLP)
        words = re.findall(r'\b[a-zA-Z]{4,}\b', all_content.lower())
        
        # Filter out common words
        common_words = {
            'that', 'this', 'with', 'from', 'they', 'have', 'been',
            'their', 'what', 'when', 'where', 'will', 'would', 'could',
            'should', 'about', 'which', 'there', 'were', 'said', 'each'
        }
        
        filtered_words = [word for word in words if word not in common_words]
        word_counts = Counter(filtered_words)
        
        # Return top themes
        return dict(word_counts.most_common(10))
    
    def _generate_statistics(self, results: List[SearchResult], themes: Dict[str, int]) -> Dict[str, Any]:
        """Generate comprehensive statistics about the results."""
        total_content_length = sum(len(result.content) for result in results)
        avg_content_length = total_content_length / len(results) if results else 0
        
        # Source distribution
        sources = Counter(result.source for result in results)
        
        # Relevance score distribution
        scores = [result.relevance_score for result in results]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        return {
            "total_results": len(results),
            "total_content_length": total_content_length,
            "average_content_length": avg_content_length,
            "average_relevance_score": avg_score,
            "top_themes": themes,
            "source_distribution": dict(sources),
            "high_quality_threshold": 0.7,
            "results_above_threshold": len([r for r in results if r.relevance_score > 0.7])
        }
    
    def get_stats(self) -> ResearchStats:
        """Get current aggregation statistics."""
        return self.stats
