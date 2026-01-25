# Cornell Lab Matchmaker

An AI-powered tool to help students find and connect with Cornell faculty researchers.

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and fill in your API keys:
   ```bash
   cp .env.example .env
   ```

## Usage

### Scraping Faculty Data
```bash
python scripts/scrape_all.py
```

### Building Embeddings
```bash
python scripts/build_embeddings.py
```

### Running the Agent
```bash
python interface/cli.py
```

### Web Interface (Optional)
```bash
streamlit run interface/streamlit_app.py
```

## Project Structure

- `config/` - Configuration and settings
- `data/` - Raw, processed, and embedding data
- `scraper/` - Web scraping and parsing logic
- `database/` - Data models and storage
- `tools/` - Agent tools for search and retrieval
- `agent/` - Main agent loop and prompts
- `interface/` - CLI and web interfaces
- `scripts/` - Utility scripts