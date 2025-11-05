"""
Tests for the search executor module.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from src.search_executor import SearchExecutor
from src.utils import SearchResult

class TestSearchExecutor:
    """Test cases for SearchExecutor."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.executor = SearchExecutor()
    
    def teardown_method(self):
        """Clean up after tests."""
        asyncio.create_task(self.executor.close())
    
    @pytest.mark.asyncio
    async def test_execute_search_success(self):
        """Test successful search execution."""
        query = "test query"
        
        # Mock progress and task_id
        mock_progress = Mock()
        mock_task_id = "test_task"
        
        # Mock HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test search result content"}}]
        }
        
        with patch.object(self.executor.client, 'post', return_value=mock_response):
            result = await self.executor.execute_search(query, mock_progress, mock_task_id)
            
            assert isinstance(result, SearchResult)
            assert result.query == query
            assert result.content == "Test search result content"
            assert result.source == "Perplexity via OpenRouter"
            mock_progress.update.assert_called_once_with(mock_task_id, advance=1)
    
    @pytest.mark.asyncio
    async def test_execute_search_failure(self):
        """Test search execution failure."""
        query = "test query"
        
        # Mock progress and task_id
        mock_progress = Mock()
        mock_task_id = "test_task"
        
        # Mock HTTP response failure
        mock_response = Mock()
        mock_response.status_code = 500
        
        with patch.object(self.executor.client, 'post', return_value=mock_response):
            result = await self.executor.execute_search(query, mock_progress, mock_task_id)
            
            assert isinstance(result, SearchResult)
            assert result.query == query
            assert "Search failed: HTTP 500" in result.content
            assert result.source == "Error"
            assert result.relevance_score == 0.0
    
    @pytest.mark.asyncio
    async def test_execute_batch_searches(self):
        """Test batch search execution."""
        queries = ["query 1", "query 2", "query 3"]
        
        # Mock progress
        mock_progress = Mock()
        mock_task_id = "test_task"
        
        # Mock individual search results
        mock_results = [
            SearchResult("query 1", "content 1", "source 1", 123456789, 0.5),
            SearchResult("query 2", "content 2", "source 2", 123456789, 0.5),
            SearchResult("query 3", "content 3", "source 3", 123456789, 0.5)
        ]
        
        with patch.object(self.executor, 'execute_search', side_effect=mock_results):
            results = await self.executor.execute_batch_searches(queries, mock_progress, mock_task_id)
            
            assert len(results) == 3
            assert all(isinstance(r, SearchResult) for r in results)
            assert self.executor.stats.total_queries == 3
