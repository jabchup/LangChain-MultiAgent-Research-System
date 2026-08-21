# LangChain Multi-Agent Research System

Orchestrates a team of LLM agents (search, reader, critic, writer) with **LangChain** + **LangGraph** to autonomously research a topic and produce a cited, structured report.

## Overview

The system decomposes a research question across specialized agents:

- **Search** — finds relevant sources for the topic
- **Reader** — extracts and summarizes key findings from each source
- **Critic** — checks claims for support, gaps, and bias
- **Writer** — synthesizes everything into a cited, structured report

## Status

🚧 Early development.

## Getting Started

```bash
pip install -r requirements.txt
```

## License

MIT
