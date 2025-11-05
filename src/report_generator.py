"""
Report generator for creating final synthesized reports using AI models.
"""

import httpx
import json
from typing import List, Dict, Any
from datetime import datetime
from rich.console import Console

from .utils import SearchResult
from .fast_ai import FastAI
from config import config

console = Console()

class ReportGenerator:
    """Generates comprehensive final reports using AI models via OpenRouter."""
    
    def __init__(self):
        self.client = httpx.Client(
            timeout=httpx.Timeout(600.0, connect=15.0),  # 10 minutes total, 15s connect
            headers={
                "Authorization": f"Bearer {config.openrouter_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://utra-deep-research.com",
                "X-Title": "ULTRA DEEP RESEARCH"
            }
        )
        self.fast_ai = FastAI()
    
    async def generate_final_report(self, topic: str, results: List[SearchResult], statistics: Dict[str, Any]) -> str:
        """Generate a comprehensive final report synthesizing all research results."""
        console.print("🎯 Generating final comprehensive report...")
        
        try:
            # Prepare the content for synthesis
            research_summary = self._prepare_research_summary(results, statistics)
            
            system_prompt = f"""
You are an expert research analyst and synthesizer. Your task is to create a comprehensive, high-signal research report based on the aggregated search results provided.

REQUIREMENTS:
1. Create a well-structured, professional report
2. Synthesize information from multiple sources into coherent insights
3. Identify key themes, patterns, and trends
4. Highlight the most important findings and discoveries
5. Provide actionable insights and conclusions
6. Organize content with clear headings and subheadings
7. Ensure the report is comprehensive yet concise
8. Focus on high-value information and signal over noise

REPORT STRUCTURE:
- Executive Summary (key findings at a glance)
- Introduction (topic overview and research scope)
- Key Findings (main discoveries and insights)
- Thematic Analysis (organized by major themes)
- Trends and Patterns (identified trends and patterns)
- Challenges and Opportunities (key challenges and opportunities)
- Conclusions (overall synthesis and conclusions)
- Implications (practical and strategic implications)

RESEARCH TOPIC: {topic}

RESEARCH STATISTICS:
- Total Sources Analyzed: {statistics.get('total_results', 0)}
- High-Quality Sources: {statistics.get('results_above_threshold', 0)}
- Average Relevance Score: {statistics.get('average_relevance_score', 0):.2f}
- Top Themes: {', '.join(list(statistics.get('top_themes', {}).keys())[:5])}

AGGREGATED RESEARCH DATA:
{research_summary}

Generate a comprehensive, insightful report that synthesizes all this information into valuable, actionable insights.
"""
            
            request_data = {
                "model": config.summarizer_model,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": f"Generate a comprehensive research report on: {topic}"
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
                report = data["choices"][0]["message"]["content"]
                
                # Add metadata header
                final_report = self._add_report_metadata(topic, report, statistics)
                
                console.print("✅ Final report generated successfully")
                return final_report
            else:
                console.print(f"❌ Failed to generate report (Status: {response.status_code})")
                return self._generate_fallback_report(topic, results, statistics)
                
        except Exception as e:
            console.print(f"❌ Exception generating report: {str(e)}")
            return self._generate_fallback_report(topic, results, statistics)
    
    def _prepare_research_summary(self, results: List[SearchResult], statistics: Dict[str, Any]) -> str:
        """Prepare a condensed summary of research results for AI synthesis."""
        # Take top results by relevance score
        top_results = sorted(results, key=lambda x: x.relevance_score, reverse=True)[:20]
        
        summary_parts = []
        for i, result in enumerate(top_results, 1):
            summary_parts.append(f"Source {i}:")
            summary_parts.append(f"Query: {result.query}")
            summary_parts.append(f"Content: {result.content[:800]}...")  # Truncate for context
            summary_parts.append(f"Relevance: {result.relevance_score:.2f}")
            summary_parts.append("---")
        
        return "\n".join(summary_parts)
    
    def _add_report_metadata(self, topic: str, report: str, statistics: Dict[str, Any]) -> str:
        """Add metadata header to the report."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        metadata = f"""
# ULTRA DEEP RESEARCH REPORT

**Topic:** {topic}
**Generated:** {timestamp}
**Research Methodology:** AI-powered multi-query search and synthesis
**Sources Analyzed:** {statistics.get('total_results', 0)}
**High-Quality Sources:** {statistics.get('results_above_threshold', 0)}
**Average Relevance Score:** {statistics.get('average_relevance_score', 0):.2f}

---

{report}

---

*Report generated by ULTRA DEEP RESEARCH - An army of AI agents for comprehensive research*
"""
        
        return metadata
    
    def _generate_fallback_report(self, topic: str, results: List[SearchResult], statistics: Dict[str, Any]) -> str:
        """Generate a fallback report when AI synthesis fails."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Simple text-based aggregation
        top_results = sorted(results, key=lambda x: x.relevance_score, reverse=True)[:10]
        
        fallback_content = f"""
# ULTRA DEEP RESEARCH REPORT (Fallback)

**Topic:** {topic}
**Generated:** {timestamp}
**Sources Analyzed:** {statistics.get('total_results', 0)}

## Key Findings

"""
        
        for i, result in enumerate(top_results, 1):
            fallback_content += f"""
### Finding {i}: {result.query}

{result.content[:500]}...

*Relevance Score: {result.relevance_score:.2f}*

"""
        
        fallback_content += f"""
## Research Statistics

- **Total Sources:** {statistics.get('total_results', 0)}
- **High-Quality Sources:** {statistics.get('results_above_threshold', 0)}
- **Average Relevance Score:** {statistics.get('average_relevance_score', 0):.2f}
- **Top Themes:** {', '.join(list(statistics.get('top_themes', {}).keys())[:5])}

---

*Fallback report generated by ULTRA DEEP RESEARCH*
"""
        
        return fallback_content
    
    async def save_report(self, report: str, topic: str = "", filename: str = None) -> str:
        """Save the report to both MD and PDF files with intelligent naming."""
        if filename is None:
            # Generate intelligent filename using FastAI
            intelligent_name = await self.fast_ai.generate_report_name(topic, report)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{intelligent_name}_{timestamp}.md"
        
        # Ensure both directories exist
        import os
        reports_dir = "reports"
        reports_pdf_dir = "reports-pdf"
        os.makedirs(reports_dir, exist_ok=True)
        os.makedirs(reports_pdf_dir, exist_ok=True)
        
        # Create full paths
        md_filepath = os.path.join(reports_dir, filename)
        pdf_filename = filename.replace('.md', '.pdf')
        pdf_filepath = os.path.join(reports_pdf_dir, pdf_filename)
        
        try:
            # Save MD file
            with open(md_filepath, 'w', encoding='utf-8') as f:
                f.write(report)
            
            console.print(f"📄 MD report saved to: {md_filepath}")
            
            # Save PDF file
            await self._save_pdf_report(report, pdf_filepath)
            
            return md_filepath
            
        except Exception as e:
            console.print(f"❌ Failed to save report: {str(e)}")
            return ""
    
    async def _save_pdf_report(self, report: str, pdf_filepath: str):
        """Convert and save report as PDF."""
        try:
            import markdown
            from weasyprint import HTML, CSS
            
            # Convert markdown to HTML
            html_content = markdown.markdown(report, extensions=['tables', 'fenced_code'])
            
            # Add basic HTML structure and styling
            full_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Research Report</title>
                <style>
                    body {{ 
                        font-family: Arial, sans-serif; 
                        line-height: 1.6; 
                        margin: 40px;
                        max-width: 800px;
                    }}
                    h1, h2, h3, h4, h5, h6 {{ 
                        color: #333; 
                        margin-top: 30px;
                    }}
                    code {{ 
                        background-color: #f4f4f4; 
                        padding: 2px 4px; 
                        border-radius: 3px;
                        font-family: monospace;
                    }}
                    pre {{ 
                        background-color: #f4f4f4; 
                        padding: 10px; 
                        border-radius: 5px;
                        overflow-x: auto;
                    }}
                    table {{ 
                        border-collapse: collapse; 
                        width: 100%;
                        margin: 20px 0;
                    }}
                    th, td {{ 
                        border: 1px solid #ddd; 
                        padding: 8px; 
                        text-align: left;
                    }}
                    th {{ 
                        background-color: #f2f2f2;
                    }}
                    blockquote {{
                        border-left: 4px solid #ccc;
                        margin: 0;
                        padding-left: 20px;
                        color: #666;
                    }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """
            
            # Convert to PDF
            HTML(string=full_html).write_pdf(pdf_filepath)
            console.print(f"📄 PDF report saved to: {pdf_filepath}")
            
        except Exception as e:
            console.print(f"❌ Failed to save PDF report: {str(e)}")
            # Don't raise exception - MD file should still be saved even if PDF fails
    
    def close(self):
        """Close the HTTP clients."""
        self.client.close()
        self.fast_ai.close()
