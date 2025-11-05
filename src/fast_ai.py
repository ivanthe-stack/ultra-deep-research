"""
Fast AI operations for quick tasks like naming, summarization, and analysis.
"""

import httpx
import re
from typing import List, Dict, Any
from rich.console import Console

from config import config

console = Console()

class FastAI:
    """Handles fast AI operations using the configured fast model."""
    
    def __init__(self):
        self.client = httpx.Client(
            timeout=httpx.Timeout(120.0, connect=15.0),  # 2 minutes total, 15s connect
            headers={
                "Authorization": f"Bearer {config.openrouter_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://utra-deep-research.com",
                "X-Title": "ULTRA DEEP RESEARCH"
            }
        )
    
    async def generate_report_name(self, topic: str, report_content: str) -> str:
        """Generate an intelligent filename for the report based on its content."""
        try:
            # Extract key themes from the report content
            content_preview = report_content[:1000] if len(report_content) > 1000 else report_content
            
            system_prompt = """You are a filename generator. Based on the research topic and report content preview, generate a concise, descriptive filename (without extension) that captures the essence of the research.

Guidelines:
- Use lowercase letters and underscores instead of spaces
- Keep it under 50 characters
- Include the main topic and key finding/theme
- Make it descriptive but not too long
- Avoid special characters except underscores
- Focus on the most important aspect of the research

Examples:
- Topic: "AI in healthcare" → "ai_healthcare_impact_analysis"
- Topic: "Climate change" → "climate_change_solutions_report"
- Topic: "Space exploration" → "space_exploration_tech_innovations" """

            request_data = {
                "model": config.fast_model,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": f"Topic: {topic}\n\nContent Preview: {content_preview}\n\nGenerate a filename:"
                    }
                ],
                
                "temperature": 0.3
            }
            
            response = self.client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                json=request_data
            )
            
            if response.status_code == 200:
                data = response.json()
                filename = data["choices"][0]["message"]["content"].strip()
                
                # Clean up the filename
                filename = re.sub(r'[^a-z0-9_]', '', filename.lower())
                filename = re.sub(r'_+', '_', filename).strip('_')
                
                # Ensure it's not empty
                if not filename:
                    filename = topic.lower().replace(' ', '_')[:30]
                
                return filename
            else:
                console.print(f"⚠️  Failed to generate intelligent filename (Status: {response.status_code})")
                return self._generate_fallback_filename(topic)
                
        except Exception as e:
            console.print(f"⚠️  Exception generating filename: {str(e)}")
            return self._generate_fallback_filename(topic)
    
    def _generate_fallback_filename(self, topic: str) -> str:
        """Generate a fallback filename when AI generation fails."""
        # Simple topic-based filename
        filename = topic.lower().replace(' ', '_')[:30]
        filename = re.sub(r'[^a-z0-9_]', '', filename)
        return filename
    
    async def extract_key_insights(self, content: str, max_insights: int = 5) -> List[str]:
        """Extract key insights from content quickly."""
        try:
            content_preview = content[:2000] if len(content) > 2000 else content
            
            system_prompt = f"""Extract the {max_insights} most important insights from this research content. Return them as a numbered list, with each insight being concise (under 100 characters)."""

            request_data = {
                "model": config.fast_model,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": content_preview
                    }
                ],
                
                "temperature": 0.2
            }
            
            response = self.client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                json=request_data
            )
            
            if response.status_code == 200:
                data = response.json()
                insights_text = data["choices"][0]["message"]["content"].strip()
                
                # Parse numbered list
                insights = []
                for line in insights_text.split('\n'):
                    line = line.strip()
                    if line and (line[0].isdigit() or line.startswith('-')):
                        # Remove numbering/bullets and clean
                        insight = re.sub(r'^\d+\.?\s*|-\s*', '', line).strip()
                        if insight:
                            insights.append(insight)
                
                return insights[:max_insights]
            else:
                return []
                
        except Exception as e:
            console.print(f"⚠️  Exception extracting insights: {str(e)}")
            return []
    
    async def generate_summary(self, content: str, max_length: int = 200) -> str:
        """Generate a quick summary of content."""
        try:
            content_preview = content[:1500] if len(content) > 1500 else content
            
            system_prompt = f"""Create a concise summary of this research content in under {max_length} characters. Focus on the main findings and key takeaways."""

            request_data = {
                "model": config.fast_model,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": content_preview
                    }
                ],
                
                "temperature": 0.3
            }
            
            response = self.client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                json=request_data
            )
            
            if response.status_code == 200:
                data = response.json()
                summary = data["choices"][0]["message"]["content"].strip()
                return summary[:max_length]
            else:
                return "Summary generation failed."
                
        except Exception as e:
            console.print(f"⚠️  Exception generating summary: {str(e)}")
            return "Summary generation failed."
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()
