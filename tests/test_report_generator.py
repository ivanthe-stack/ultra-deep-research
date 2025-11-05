"""
Tests for the report generator module.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch

from src.report_generator import ReportGenerator
from src.utils import SearchResult

class TestReportGenerator:
    """Test cases for ReportGenerator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.generator = ReportGenerator()
    
    def teardown_method(self):
        """Clean up after tests."""
        self.generator.close()
    
    @pytest.mark.asyncio
    async def test_generate_final_report(self):
        """Test final report generation."""
        topic = "test topic"
        
        # Mock search results
        results = [
            SearchResult("query 1", "content 1 with research findings", "source 1", 123456789, 0.8),
            SearchResult("query 2", "content 2 with analysis data", "source 2", 123456789, 0.7)
        ]
        
        statistics = {
            "total_results": 2,
            "average_relevance_score": 0.75,
            "top_themes": {"research": 2, "analysis": 1}
        }
        
        # Mock HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "# Test Report\n\nThis is a comprehensive report..."}}]
        }
        
        with patch.object(self.generator.client, 'post', return_value=mock_response):
            report = await self.generator.generate_final_report(topic, results, statistics)
            
            assert "# ULTRA DEEP RESEARCH REPORT" in report
            assert topic in report
            assert "Test Report" in report
    
    @pytest.mark.asyncio
    async def test_save_report(self):
        """Test report saving functionality."""
        report_content = "# Test Report\n\nThis is a test report."
        filename = "test_report.md"
        
        # Mock file writing
        with patch("builtins.open", create=True) as mock_file:
            mock_file.return_value.__enter__.return_value.write = Mock()
            
            saved_filename = await self.generator.save_report(report_content, filename)
            
            assert saved_filename == filename
            mock_file.assert_called_once_with(filename, 'w', encoding='utf-8')
    
    def test_generate_fallback_report(self):
        """Test fallback report generation."""
        topic = "test topic"
        
        results = [
            SearchResult("query 1", "content 1", "source 1", 123456789, 0.8),
            SearchResult("query 2", "content 2", "source 2", 123456789, 0.7)
        ]
        
        statistics = {
            "total_results": 2,
            "average_relevance_score": 0.75
        }
        
        fallback_report = self.generator._generate_fallback_report(topic, results, statistics)
        
        assert "# ULTRA DEEP RESEARCH REPORT (Fallback)" in fallback_report
        assert topic in fallback_report
        assert "content 1" in fallback_report
        assert "content 2" in fallback_report
