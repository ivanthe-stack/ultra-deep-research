"""
ULTRA DEEP RESEARCH - Main CLI Application
An army of AI agents for comprehensive research and analysis.
"""

import asyncio
import click
import time
from rich.console import Console

from src.cli_formatter import CLIFormatter
from src.query_generator import QueryGenerator
from src.search_executor import SearchExecutor
from src.result_aggregator import ResultAggregator
from src.report_generator import ReportGenerator
from config import config

console = Console()

def clean_topic(topic: str) -> str:
    """Clean and normalize the topic input."""
    # Remove all line breaks and normalize spaces
    topic = topic.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    # Remove extra whitespace
    topic = ' '.join(topic.split())
    # Remove problematic characters that might break CLI
    topic = topic.replace('"', "'").replace('`', '')
    # Remove multiple spaces again
    topic = ' '.join(topic.split())
    return topic.strip()

@click.command()
@click.argument('topic', type=str)
@click.option('--output', '-o', type=str, help='Output filename for the report (saved in reports folder)')
@click.option('--queries', '-q', type=int, help='Number of queries to generate (default: from config)')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--save-steps', is_flag=True, help='Save intermediate steps')
def research(topic: str, output: str, queries: int, verbose: bool, save_steps: bool):
    """
    🚀 ULTRA DEEP RESEARCH - Comprehensive AI-powered research
    
    TOPIC: The research topic you want to investigate
    """
    
    # Clean the topic input
    topic = clean_topic(topic)
    
    # Initialize CLI formatter
    formatter = CLIFormatter()
    formatter.print_welcome()
    
    # Validate configuration
    if not config.validate():
        formatter.print_error("Configuration validation failed. Please check your .env file.")
        return
    
    # Override config with command line options
    if queries:
        config.num_queries = queries
    
    # Print configuration
    if verbose:
        formatter.print_config(config)
    
    # Run the research pipeline
    asyncio.run(run_research_pipeline(topic, output, formatter, verbose, save_steps))

async def run_research_pipeline(topic: str, output: str, formatter: CLIFormatter, verbose: bool, save_steps: bool):
    """Execute the complete research pipeline."""
    
    # Initialize components
    query_generator = QueryGenerator()
    search_executor = SearchExecutor()
    result_aggregator = ResultAggregator()
    report_generator = ReportGenerator()
    
    # Create progress tracker
    progress = formatter.create_progress()
    
    try:
        # Start research without progress tracking
        # Stage 1: Initial Context Search
            formatter.print_stage_start("Initial Context Search", 1, 5)
            task_1 = formatter.add_stage_task("🔍 Initial Context Search", 1)
            
            try:
                initial_query = await query_generator.generate_initial_search_query(topic)
                formatter.print_info(f"Generated initial search query: {initial_query}")
                
                # Execute initial search
                initial_results = await search_executor.execute_batch_searches(
                    [initial_query]
                )
                
                context = initial_results[0].content if initial_results else ""
                formatter.complete_task("🔍 Initial Context Search")
                formatter.print_stage_complete("Initial Context Search", f"Context gathered")
                
            except Exception as e:
                formatter.print_error(f"Initial search failed: {str(e)}")
                context = ""
            
            # Stage 2: Query Generation
            formatter.print_stage_start("Query Generation", 2, 5)
            task_2 = formatter.add_stage_task("🧠 Generating Queries", 1)
            
            try:
                queries = await query_generator.generate_diverse_queries(topic, context)
                formatter.print_info(f"Generated {len(queries)} diverse search queries")
                formatter.complete_task("🧠 Generating Queries")
                formatter.print_stage_complete("Query Generation", f"{len(queries)} queries created")
                
                if save_steps:
                    await save_queries_to_file(queries, topic)
                
            except Exception as e:
                formatter.print_error(f"Query generation failed: {str(e)}")
                return
            
            # Stage 3: Search Execution
            formatter.print_stage_start("Search Execution", 3, 5)
            task_3 = formatter.add_stage_task("⚡ Executing Searches", len(queries))
            
            try:
                search_results = await search_executor.execute_batch_searches(
                    queries
                )
                
                search_stats = search_executor.get_stats()
                formatter.complete_task("⚡ Executing Searches")
                formatter.print_stage_complete("Search Execution", 
                    f"{search_stats.completed_searches}/{search_stats.total_queries} completed")
                
            except Exception as e:
                formatter.print_error(f"Search execution failed: {str(e)}")
                return
            
            # Stage 4: Result Aggregation
            formatter.print_stage_start("Result Aggregation", 4, 5)
            task_4 = formatter.add_stage_task("📊 Aggregating Results", 1)
            
            try:
                aggregated_results, statistics = result_aggregator.aggregate_results(search_results)
                formatter.complete_task("📊 Aggregating Results")
                formatter.print_stage_complete("Result Aggregation", 
                    f"{len(aggregated_results)} high-quality results")
                
            except Exception as e:
                formatter.print_error(f"Result aggregation failed: {str(e)}")
                return
            
            # Stage 5: Report Generation
            formatter.print_stage_start("Report Generation", 5, 5)
            task_5 = formatter.add_stage_task("🎯 Generating Report", 1)
            
            try:
                final_report = await report_generator.generate_final_report(
                    topic, aggregated_results, statistics
                )
                formatter.complete_task("🎯 Generating Report")
                formatter.print_stage_complete("Report Generation", "Comprehensive report created")
                
            except Exception as e:
                formatter.print_error(f"Report generation failed: {str(e)}")
                return
            
            # Save report
            report_file = await report_generator.save_report(final_report, topic, output)
            
            # Print final statistics
            formatter.print_statistics(search_stats.__dict__, statistics)
            
            # Print final summary
            total_time = time.time() - (formatter.start_time or time.time())
            formatter.print_final_summary(topic, report_file, total_time)
            
    except KeyboardInterrupt:
        formatter.print_warning("Research interrupted by user")
    except Exception as e:
        formatter.print_error(f"Unexpected error: {str(e)}")
    finally:
        # Cleanup
        await search_executor.close()
        query_generator.close()
        report_generator.close()
        formatter.cleanup()

async def save_queries_to_file(queries: list, topic: str):
    """Save generated queries to a file for debugging."""
    import os
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"queries_{topic.replace(' ', '_')}_{timestamp}.txt"
    
    # Ensure reports directory exists
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)
    
    # Create full path
    filepath = os.path.join(reports_dir, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Generated Queries for: {topic}\n")
            f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Queries: {len(queries)}\n")
            f.write("=" * 50 + "\n\n")
            
            for i, query in enumerate(queries, 1):
                f.write(f"{i}. {query}\n")
        
        console.print(f"📄 Queries saved to: {filepath}")
    except Exception as e:
        console.print(f"⚠️  Failed to save queries: {str(e)}")

if __name__ == "__main__":
    research()
