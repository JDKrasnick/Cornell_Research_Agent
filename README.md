# Cornell Lab Matchmaker

<div align="center">

**An AI-powered research matchmaking tool that connects Cornell students with faculty researchers through intelligent semantic search and personalized outreach.**

[Features](#features) • [Tech Stack](#tech-stack) • [Installation](#installation) • [Usage](#usage) • [Project Structure](#project-structure)

</div>

---

## Problem Statement

Finding the right research lab or faculty advisor is one of the most critical decisions for undergraduate and graduate students, yet it remains a manual and time-consuming process:

- **Information Overload**: Hundreds of faculty across dozens of departments make it difficult to identify relevant researchers
- **Hidden Connections**: Students may miss ideal matches because faculty expertise isn't obvious from titles alone
- **Cold Outreach Challenges**: Crafting personalized, compelling emails to professors requires significant research and effort
- **Fragmented Information**: Faculty data is scattered across department pages, lab websites, and publication databases

Cornell Lab Matchmaker solves these problems by combining web scraping, semantic search, and AI-powered tools to help students discover relevant research opportunities and craft personalized outreach emails.

---

## Features

### Intelligent Faculty Search
- **Semantic Search**: Find faculty based on research interests, not just keywords
- **Publication-Enhanced Matching**: Search incorporates faculty publications for deeper context
- **Multi-Source Data**: Aggregates information from department pages, lab websites, and academic databases

### Research Discovery
- **Publication Search**: Explore faculty research through their papers and citations
- **Lab Website Analysis**: Automatically fetch and analyze lab pages for current projects
- **Interest-Based Recommendations**: Get faculty suggestions based on your academic background

### Personalized Outreach
- **AI-Powered Email Drafting**: Generate customized outreach emails based on:
  - Your academic background and interests
  - Faculty's research areas and recent publications
  - Specific projects or papers you're interested in
- **Context-Aware Templates**: Emails reference specific work to demonstrate genuine interest

### Multiple Interfaces
- **Interactive CLI**: Conversational chat interface for exploration
- **Batch Commands**: Direct search, details lookup, and email generation
- **Web Interface**: Streamlit-based GUI for visual exploration (optional)

---

## Tech Stack

### Core Technologies
- **Python 3.9+** - Main programming language
- **SQLite** - Local database for faculty and publication data
- **ChromaDB** - Vector database for semantic search

### AI & Machine Learning
- **OpenAI GPT-4o** - LLM for agent reasoning and email generation
- **Anthropic Claude** - Alternative LLM provider
- **Sentence Transformers** - Local embeddings (`all-MiniLM-L6-v2`)
- **OpenAI Embeddings** - Cloud embeddings (`text-embedding-3-small`)

### Data Collection
- **BeautifulSoup4** - HTML parsing
- **Requests** - HTTP client
- **HTTPX** - Async HTTP support
- **Semantic Scholar API** - Academic publication data

### Interface & UX
- **Rich** - Beautiful CLI formatting
- **Streamlit** - Web interface
- **Pydantic** - Data validation
- **SQLAlchemy** - Database ORM

---

## Installation

### Prerequisites
- Python 3.9 or higher
- OpenAI API key (required)
- Anthropic API key (optional)
- Semantic Scholar API key (optional, for higher rate limits)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/Cornell_Research_Agent.git
   cd Cornell_Research_Agent
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your API keys:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here  # Optional
   SEMANTIC_SCHOLAR_API_KEY=your_key_here         # Optional
   ```

5. **Initialize the database**
   ```bash
   # Scrape faculty data
   python scripts/scrape_all.py

   # Build semantic search embeddings
   python scripts/build_embeddings.py
   ```

---

## Usage

### Interactive Chat Mode

Start a conversational session with the agent:

```bash
python main.py chat
```

Example interactions:
```
You: I'm interested in machine learning and robotics
Agent: I found 5 faculty members working on ML and robotics...

You: Tell me more about Professor Smith
Agent: [Detailed information about research, publications, lab...]

You: Draft an email to Professor Smith
Agent: [Generates personalized email based on your interests]
```

### Batch Commands

**Search for faculty:**
```bash
python main.py search "natural language processing"
python main.py search "quantum computing" --limit 10
```

**Get faculty details:**
```bash
python main.py details <faculty_id>
```

**Draft outreach email:**
```bash
python main.py draft <faculty_id> \
  --student-name "Jane Doe" \
  --background "CS senior interested in ML" \
  --interests "explainable AI and fairness in machine learning"
```

**Configuration:**
```bash
python main.py config show              # View current settings
python main.py config set llm gpt-4o    # Change LLM model
python main.py config set verbose true  # Enable verbose mode
```

### Web Interface (Optional)

Launch the Streamlit web app:
```bash
streamlit run interface/streamlit_app.py
```

### Advanced Options

**Build embeddings with custom settings:**
```bash
# Include top 10 publications per faculty
python scripts/build_embeddings.py --max-publications 10

# Exclude publications (faster, less accurate)
python scripts/build_embeddings.py --no-publications
```

**Control output verbosity:**
```bash
python main.py search "ML" --verbose  # Show all tool executions
python main.py search "ML" --quiet    # Minimal output
python main.py search "ML" --json     # JSON output
```

---

## Project Structure

```
Cornell_Research_Agent/
├── agent/              # AI agent logic and prompts
│   ├── prompts.py      # System prompts and templates
│   └── runner.py       # Agent execution loop
├── config/             # Configuration and settings
│   └── settings.py     # Global configuration
├── data/               # Data storage
│   ├── database.sqlite # Faculty and publication data
│   └── embeddings/     # ChromaDB vector store
├── interface/          # User interfaces
│   ├── cli_app.py      # Main CLI application
│   ├── streamlit_app.py # Web interface
│   ├── commands/       # CLI subcommands
│   └── output/         # Display formatters
├── scraper/            # Data collection
│   └── sources/        # Faculty and publication scrapers
├── scripts/            # Utility scripts
│   ├── scrape_all.py   # Data collection pipeline
│   └── build_embeddings.py # Vector index builder
├── tools/              # Agent tools
│   ├── search_faculty.py      # Semantic faculty search
│   ├── search_publications.py # Publication lookup
│   ├── get_faculty_details.py # Detailed info retrieval
│   ├── draft_email.py         # Email generation
│   └── fetch_webpage.py       # Web scraping tool
├── tests/              # Unit tests
├── main.py             # Application entry point
└── requirements.txt    # Python dependencies
```

---

## How It Works

1. **Data Collection**: Scrapes Cornell faculty pages and enriches with publication data from Semantic Scholar
2. **Embedding Generation**: Creates semantic embeddings of faculty research interests and publications
3. **Semantic Search**: Uses vector similarity to find relevant faculty based on natural language queries
4. **Agent Reasoning**: GPT-4o agent uses tools to search, explore, and synthesize information
5. **Personalized Output**: Generates customized emails and recommendations based on user context

---

## Contributing

Contributions are welcome! Areas for improvement:

- Add more Cornell departments and sources
- Implement faculty availability/recruiting status detection
- Add support for more universities
- Improve email template variety
- Add unit tests for agent tools

---

## License

This project is for educational purposes. Please respect faculty privacy and use responsibly when conducting outreach.

---

## Acknowledgments

- Cornell University for publicly available faculty information
- Semantic Scholar for providing publication data
- OpenAI and Anthropic for LLM capabilities

---

<div align="center">
Made with ❤️ for Cornell students seeking research opportunities
</div>
