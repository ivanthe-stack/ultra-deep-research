# ULTRA DEEP RESEARCH 🚀

An army of AI agents that does 100+ different search queries for any topic you want to research, using multiple deep research and AI search APIs, and aggregates an ultra-high-signal report with the best ideas & insights.

## Features

- 🔍 **Context-Aware Query Generation**: Uses AI to generate diverse, comprehensive search queries
- ⚡ **Async Search Execution**: Dispatches 100+ concurrent searches via Perplexity API
- 📊 **Smart Result Aggregation**: Filters, deduplicates, and ranks results for quality
- 🎯 **AI-Powered Synthesis**: Creates comprehensive reports using advanced reasoning models
- 🎨 **Rich CLI Interface**: Beautiful progress tracking with emojis and detailed statistics
- 🔧 **Flexible Configuration**: Customizable models, query counts, and search parameters

## Quick Start

### 1. Setup Environment

```bash
# Clone and navigate to the project
cd utra-deep-research

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
# Copy the environment template
cp .env.example .env

# Edit .env with your configuration
nano .env
```

**Required Configuration:**
- `OPENROUTER_API_KEY`: Your OpenRouter API key
- `INIT_SEARCH_MODEL`: Model for initial context search (default: claude-3-haiku)
- `QUERY_MODEL`: Model for generating queries (default: claude-3-haiku-4.5)
- `SUMMARIZER_MODEL`: Model for final synthesis (default: claude-3-sonnet-4.5)
- `NUM_QUERIES`: Number of queries to generate (default: 100)

### 3. Run Research

```bash
# Basic usage
python main.py "artificial intelligence in healthcare"

# With custom output file
python main.py "climate change solutions" -o climate_report.md

# With custom query count
python main.py "blockchain technology" -q 50

# Verbose output with intermediate steps saved
python main.py "space exploration" -v --save-steps
```

## Architecture

```
utra-deep-research/
├── main.py                 # CLI entry point
├── config.py              # Configuration management
├── .env.example           # Environment variables template
├── requirements.txt       # Python dependencies
├── src/
│   ├── query_generator.py  # AI-powered query generation
│   ├── search_executor.py  # Async search execution
│   ├── result_aggregator.py # Result processing and ranking
│   ├── report_generator.py # Final report synthesis
│   ├── cli_formatter.py    # Rich CLI interface
│   └── utils.py           # Helper functions
├── reports/               # Generated research reports
├── tests/                 # Unit tests
└── examples/              # Sample outputs
```

## Research Pipeline

1. **🔍 Initial Context Search**: Gathers preliminary context using a broad search query
2. **🧠 Query Generation**: Creates 100+ diverse search queries based on context
3. **⚡ Async Search Execution**: Dispatches all queries concurrently via Perplexity API
4. **📊 Result Aggregation**: Processes, filters, and ranks results for quality
5. **🎯 Report Generation**: Synthesizes findings into a comprehensive report

## CLI Options

- `TOPIC`: Research topic (required)
- `-o, --output`: Custom output filename
- `-q, --queries`: Number of queries to generate
- `-v, --verbose`: Enable detailed output
- `--save-steps`: Save intermediate queries and results

## Example Output

The CLI provides rich progress tracking:

```
🚀 ULTRA DEEP RESEARCH Starting...
🔍 [1/5] Initial Context Search... ✅
🧠 [2/5] Generating 100 Queries... ████████████████████ 100% ✅
⚡ [3/5] Executing 100 Searches... ████████████████ 75% 🔄
📊 [4/5] Aggregating Results... ⏳
🎯 [5/5] Generating Final Report... ⏳

📈 Statistics:
• Queries Generated: 100
• Searches Completed: 75/100
• High-Quality Results: 42
• Processing Time: 2m 15s
```

## Requirements

- Python 3.12+
- OpenRouter API key
- Internet connection for API calls

## Dependencies

- `httpx`: Async HTTP client
- `click`: CLI framework
- `rich`: Rich terminal output
- `python-dotenv`: Environment variable management
- `asyncio`: Async programming support

## Testing

Run the test suite:

```bash
source venv/bin/activate
python -m pytest tests/ -v
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENROUTER_API_KEY` | OpenRouter API key | Required |
| `INIT_SEARCH_MODEL` | Initial search model | claude-3-haiku |
| `QUERY_MODEL` | Query generation model | claude-3-haiku-4.5 |
| `SUMMARIZER_MODEL` | Report synthesis model | claude-3-sonnet-4.5 |
| `NUM_QUERIES` | Number of queries to generate | 100 |
| `MAX_CONCURRENT_SEARCHES` | Concurrent search limit | 10 |
| `SEARCH_TIMEOUT` | Search timeout (seconds) | 30 |
| `API_RATE_LIMIT` | API rate limit (calls/minute) | 60 |

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit issues and enhancement requests.

---

*Built with ❤️ by ULTRA DEEP RESEARCH - An army of AI agents for comprehensive research*
