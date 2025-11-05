"""
Query generator for creating diverse search queries using AI models.
"""

import httpx
import json
from typing import List, Dict, Any
from rich.console import Console

from config import config

console = Console()

class QueryGenerator:
    """Generates diverse search queries using AI models via OpenRouter."""
    
    def __init__(self):
        self.client = httpx.Client(
            timeout=httpx.Timeout(300.0, connect=15.0),  # 5 minutes total, 15s connect
            headers={
                "Authorization": f"Bearer {config.openrouter_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://utra-deep-research.com",
                "X-Title": "ULTRA DEEP RESEARCH"
            }
        )
    
    async def generate_initial_search_query(self, topic: str) -> str:
        """Generate an initial search query for context gathering."""
        try:
            request_data = {
                "model": config.init_search_model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a research assistant. Generate a comprehensive, broad search query that will help gather initial context about the given topic. The query should be designed to get a good overview of the subject."
                    },
                    {
                        "role": "user",
                        "content": f"Generate a broad search query for research about: {topic}"
                    }
                ],
                "max_tokens": 200,
                "temperature": 0.3
            }
            
            response = self.client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                json=request_data
            )
            
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"].strip()
            else:
                console.print(f"❌ Failed to generate initial search query (Status: {response.status_code})")
                return f"Comprehensive overview of {topic}"
                
        except Exception as e:
            console.print(f"❌ Exception generating initial search query: {str(e)}")
            return f"Comprehensive overview of {topic}"
    
    async def generate_diverse_queries(self, topic: str, context: str = "") -> List[str]:
        """Generate diverse search queries based on topic and context."""
        try:
            console.print(f"Generating {config.num_queries} queries for topic: {topic[:50]}...")
            
            # Truncate very long topics to prevent API issues
            safe_topic = topic[:200] + "..." if len(topic) > 200 else topic
            safe_context = context[:500] + "..." if len(context) > 500 else context
            
            system_prompt = f"""
You are an expert research query generator. Your task is to generate {config.num_queries} diverse, comprehensive search queries about the given topic.

Guidelines:
1. Create queries from different angles and perspectives
2. Include technical, business, academic, and practical viewpoints
3. Vary query complexity from basic to advanced
4. Cover historical context, current state, and future trends
5. Include queries about challenges, opportunities, and solutions
6. Consider different stakeholders and use cases
7. Mix broad overview queries with specific niche queries
8. Include comparative and analytical queries
9. Add queries about recent developments and news
10. Consider geographical and cultural variations

Context from initial research: {safe_context if safe_context else "No context available"}

Topic: {safe_topic}

Generate exactly {config.num_queries} diverse search queries, one per line. Each query should be unique and valuable for comprehensive research.
Keep each query under 100 characters.
"""
            
            request_data = {
                "model": config.query_model,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": f"Generate {config.num_queries} diverse search queries for comprehensive research about: {safe_topic}"
                    }
                ],
                
                "temperature": 0.7
            }
            
            console.print("Calling query generation API...")
            response = self.client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                json=request_data
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                
                # Parse the response into individual queries
                queries = []
                for line in content.strip().split('\n'):
                    line = line.strip()
                    # Remove numbering if present
                    if line and not line.startswith('#'):
                        # Remove common numbering patterns
                        cleaned_line = line
                        for prefix in ['1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.',
                                      '•', '-', '*', 'Query:', 'Search:']:
                            if cleaned_line.startswith(prefix):
                                cleaned_line = cleaned_line[len(prefix):].strip()
                                break
                        
                        if cleaned_line and len(cleaned_line) > 10:  # Filter out very short queries
                            queries.append(cleaned_line)
                
                # Ensure we have the right number of queries
                if len(queries) < config.num_queries:
                    console.print(f"⚠️  Generated {len(queries)} queries, expected {config.num_queries}")
                elif len(queries) > config.num_queries:
                    queries = queries[:config.num_queries]
                
                console.print(f"✅ Generated {len(queries)} diverse search queries")
                return queries
                
            else:
                console.print(f"❌ Failed to generate queries (Status: {response.status_code})")
                return self._generate_fallback_queries(topic)
                
        except Exception as e:
            console.print(f"❌ Exception generating queries: {str(e)}")
            console.print("🔄 Using fallback query generation...")
            return self._generate_fallback_queries(topic)
    
    def _generate_fallback_queries(self, topic: str) -> List[str]:
        """Generate fallback queries when AI generation fails."""
        # Truncate topic for fallback queries to prevent issues
        safe_topic = topic[:100] + "..." if len(topic) > 100 else topic
        
        base_queries = [
            f"What is {safe_topic} and how does it work",
            f"History and evolution of {safe_topic}",
            f"Current trends in {safe_topic}",
            f"Future of {safe_topic}",
            f"Benefits and advantages of {safe_topic}",
            f"Challenges and limitations of {safe_topic}",
            f"Best practices for {safe_topic}",
            f"Use cases and applications of {safe_topic}",
            f"Comparison of {safe_topic} alternatives",
            f"Implementation strategies for {safe_topic}",
            f"Industry impact of {safe_topic}",
            f"Economic aspects of {safe_topic}",
            f"Technical details of {safe_topic}",
            f"Research and development in {safe_topic}",
            f"Expert opinions on {safe_topic}",
            f"Case studies involving {safe_topic}",
            f"Recent news about {safe_topic}",
            f"Market analysis of {safe_topic}",
            f"Regulatory aspects of {safe_topic}",
            f"Environmental impact of {safe_topic}"
        ]
        
        # Extend with variations to reach the desired number
        queries = []
        for i in range(config.num_queries):
            base_query = base_queries[i % len(base_queries)]
            if i >= len(base_queries):
                # Add variations for extra queries
                queries.append(f"{base_query} - Advanced perspective")
            else:
                queries.append(base_query)
        
        return queries[:config.num_queries]
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()
