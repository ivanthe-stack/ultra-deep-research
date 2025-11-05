"""
Tests for the query generator module.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch

from src.query_generator import QueryGenerator
from config import config

class TestQueryGenerator:
    """Test cases for QueryGenerator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.generator = QueryGenerator()
    
    def teardown_method(self):
        """Clean up after tests."""
        self.generator.close()
    
    @pytest.mark.asyncio
    async def test_generate_initial_search_query(self):
        """Test initial search query generation."""
        topic = "artificial intelligence"
        
        # Mock the HTTP client response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Comprehensive overview of artificial intelligence"}}]
        }
        
        with patch.object(self.generator.client, 'post', return_value=mock_response):
            query = await self.generator.generate_initial_search_query(topic)
            
            assert query == "Comprehensive overview of artificial intelligence"
    
    @pytest.mark.asyncio
    async def test_generate_diverse_queries(self):
        """Test diverse query generation."""
        topic = "machine learning"
        context = "Machine learning is a subset of AI"
        
        # Mock response with multiple queries
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "What is machine learning?\nHow does machine learning work?\nHistory of machine learning"}}]
        }
        
        with patch.object(self.generator.client, 'post', return_value=mock_response):
            queries = await self.generator.generate_diverse_queries(topic, context)
            
            assert len(queries) > 0
            assert all(isinstance(q, str) for q in queries)
            assert all(len(q.strip()) > 0 for q in queries)
    
    def test_generate_fallback_queries(self):
        """Test fallback query generation."""
        topic = "blockchain technology"
        
        queries = self.generator._generate_fallback_queries(topic)
        
        assert len(queries) == config.num_queries
        assert all(topic.lower() in q.lower() for q in queries)
        assert all(isinstance(q, str) for q in queries)
