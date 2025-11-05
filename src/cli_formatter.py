"""
Rich CLI formatter for beautiful output with emojis and progress bars.
"""

import time
from typing import Dict, Any
from rich.console import Console
from rich.progress import Progress, TaskID, BarColumn, TextColumn, TimeRemainingColumn, TimeElapsedColumn
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

console = Console()

class CLIFormatter:
    """Handles rich CLI formatting with emojis and progress tracking."""
    
    def __init__(self):
        self.progress = None
        self.tasks = {}
        self.start_time = None
    
    def print_welcome(self):
        """Print minimal welcome message."""
        console.print("🔍 ULTRA DEEP RESEARCH", style="bold blue")
    
    def print_config(self, config):
        """Print current configuration."""
        console.print(f"Models: {config.init_search_model} → {config.query_model} → {config.search_model} → {config.summarizer_model}")
        console.print(f"Queries: {config.num_queries} | Concurrency: {config.max_concurrent_searches}")
    
    def create_progress(self):
        """Create a minimal progress tracker."""
        self.progress = None
        self.start_time = time.time()
        return None
    
    def add_stage_task(self, description: str, total: int = 100):
        """Add a new stage task to progress tracking."""
        self.current_total = total
        self.current_completed = 0
        return total
    
    def update_task(self, description: str, advance: int = 1, **kwargs):
        """Update a specific task progress."""
        self.current_completed += advance
    
    def complete_task(self, description: str):
        """Mark a task as complete."""
        self.current_completed = self.current_total
    
    def print_stage_start(self, stage_name: str, stage_num: int, total_stages: int):
        """Print the start of a new stage."""
        stage_details = {
            "🔍 Initial Context Search": "🔍 Initial context search",
            "🧠 Query Generation": "🧠 Generating diverse queries",
            "⚡ Search Execution": "⚡ Executing async searches",
            "📊 Result Aggregation": "📊 Aggregating results",
            "🎯 Report Generation": "🎯 Generating final report"
        }
        
        detail = stage_details.get(stage_name, f"🔄 {stage_name}")
        console.print(f"[{stage_num}/{total_stages}] {detail}")
    
    def print_stage_complete(self, stage_name: str, details: str = ""):
        """Print the completion of a stage."""
        if details:
            console.print(f"✅ {details}")
        else:
            console.print("✅ Done")
    
    def print_statistics(self, stats: Dict[str, Any], execution_stats: Dict[str, Any] = None):
        """Print clean statistics."""
        completed = stats.get('completed_searches', 0)
        total = stats.get('total_queries', 0)
        failed = stats.get('failed_searches', 0)
        
        console.print(f"Searches: {completed}/{total} completed")
        
        if execution_stats:
            results = execution_stats.get('total_results', 0)
            avg_score = execution_stats.get('average_relevance_score', 0)
            console.print(f"Results: {results} | Quality: {avg_score:.2f}")
        
        # Processing time
        if stats.get('processing_time', 0) > 0:
            processing_time = stats['processing_time']
            if processing_time < 60:
                time_str = f"{processing_time:.1f}s"
            else:
                minutes = int(processing_time // 60)
                seconds = int(processing_time % 60)
                time_str = f"{minutes}m {seconds}s"
            console.print(f"Time: {time_str}")
    
    def print_error(self, message: str):
        """Print an error message."""
        console.print(f"❌ {message}")
    
    def print_warning(self, message: str):
        """Print a warning message."""
        console.print(f"⚠️  {message}")
    
    def print_success(self, message: str):
        """Print a success message."""
        console.print(f"✅ {message}")
    
    def print_info(self, message: str):
        """Print an info message."""
        console.print(f"ℹ️  {message}")
    
    def print_final_summary(self, topic: str, report_file: str, total_time: float):
        """Print final summary with report location."""
        if total_time < 60:
            time_str = f"{total_time:.0f}s"
        else:
            minutes = int(total_time // 60)
            seconds = int(total_time % 60)
            time_str = f"{minutes}m {seconds}s"
        
        console.print(f"✅ Research complete: {report_file} ({time_str})")
    
    def cleanup(self):
        """Clean up progress tracking."""
        self.progress = None
