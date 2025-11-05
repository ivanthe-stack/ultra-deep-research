"""
Configuration management for ULTRA DEEP RESEARCH.
"""

import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the application."""
    
    def __init__(self):
        self.openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
        self.init_search_model: str = os.getenv("INIT_SEARCH_MODEL", "claude-3-haiku")
        self.query_model: str = os.getenv("QUERY_MODEL", "claude-3-haiku-4.5")
        self.search_model: str = os.getenv("SEARCH_MODEL", "perplexity/sonar-pro")
        self.summarizer_model: str = os.getenv("SUMMARIZER_MODEL", "claude-3-sonnet-4.5")
        self.fast_model: str = os.getenv("FAST_MODEL", "anthropic/claude-haiku")
        self.num_queries: int = int(os.getenv("NUM_QUERIES", "100"))
        self.max_concurrent_searches: int = int(os.getenv("MAX_CONCURRENT_SEARCHES", "10"))
        self.search_timeout: int = int(os.getenv("SEARCH_TIMEOUT", "30"))
        self.api_rate_limit: int = int(os.getenv("API_RATE_LIMIT", "60"))
    
    def validate(self) -> bool:
        """Validate configuration settings."""
        if not self.openrouter_api_key:
            print("❌ OPENROUTER_API_KEY is required!")
            return False
        if self.num_queries < 1:
            print("❌ NUM_QUERIES must be at least 1!")
            return False
        if self.max_concurrent_searches < 1:
            print("❌ MAX_CONCURRENT_SEARCHES must be at least 1!")
            return False
        return True
    
    def print_config(self):
        """Print current configuration for debugging."""
        print(f"🔧 Configuration:")
        print(f"   • Init Search Model: {self.init_search_model}")
        print(f"   • Query Model: {self.query_model}")
        print(f"   • Search Model: {self.search_model}")
        print(f"   • Summarizer Model: {self.summarizer_model}")
        print(f"   • Fast Model: {self.fast_model}")
        print(f"   • Number of Queries: {self.num_queries}")
        print(f"   • Max Concurrent Searches: {self.max_concurrent_searches}")
        print(f"   • Search Timeout: {self.search_timeout}s")

# Global config instance
config = Config()
