# Deep Research Agent

A powerful multi-agent research system built using OpenAI Agents SDK and Firecrawl. This application performs comprehensive web research on any topic, analyzing multiple sources and producing in-depth reports.

## Features

- **Multi-Agent Architecture**: Uses two specialized agents - Research Agent and Elaboration Agent
- **Deep Web Research**: Automatically searches the web, extracts content, and synthesizes findings
- **Enhanced Analysis**: Second agent elaborates on initial research with additional context
- **Interactive UI**: Clean Streamlit interface for easy interaction
- **Downloadable Reports**: Export research findings as markdown files

## Setup

1. Clone this repository:
```
git clone [repository URL]
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Set up your API keys:
   - Create an account at [OpenAI](https://platform.openai.com/) and get your API key
   - Create an account at [Firecrawl](https://www.firecrawl.dev/) and get your API key
   - Add your API keys to the `.env` file or input them directly in the app

4. Run the application:
```
streamlit run deep_research_openai.py
```

## Usage

1. Enter your OpenAI and Firecrawl API keys in the sidebar (if not already set in `.env`)
2. Enter a research topic in the main input field
3. Adjust advanced settings if desired
4. Click "Start Multi-Agent Research" to begin the process
5. Wait for the research process to complete
6. View and download the enhanced research report

## Credits

Inspired by the tutorial from [Unwind AI](https://www.theunwindai.com/p/build-a-deep-research-agent-with-openai-agents-sdk-and-firecrawl)
