<!--
 * @Author: Haodong Chen chd243013@gmail.com
 * @Date: 2025-05-07 23:36:52
 * @LastEditors: Haodong Chen chd243013@gmail.com
 * @LastEditTime: 2025-05-07 23:38:15
 * @FilePath: /OpenBioLLM-RAG/openbio_rag/README.md
 * @Description: This is the default setting, please set `customMade`, open koroFileHeader for configuration: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
-->
# OpenBioLLM

An Agentic RAG system based on LangChain for intelligent Q&A in the field of bioinformatics.

## Features

- Multi-Agent collaborative intelligent Q&A system
- Workflow based on LangChain and LangGraph
- Support for web search and knowledge base retrieval
- Flexible decision-making and evaluation mechanisms

## Installation

```bash
# Clone the project
git clone [your-repo-url]
cd openbio_rag

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit the .env file and fill in your API keys
```

## Usage

```python
from src.graph.workflow import RAGWorkflow

# Create workflow
workflow = RAGWorkflow()
app = workflow.create_graph()

# Run query
result = app.invoke({
    "messages": ["Your question"],
    "next_step": "decide",
    "action_history": [],
    "current_result": "",
    "attempts": 0
})
```

## Project Structure

```
openbio_rag/
├── notebooks/          # Jupyter notebooks
├── src/                # Source code
│   ├── agents/         # Agent implementations
│   ├── types/          # Type definitions
│   ├── tools/          # Tool collections
│   ├── prompts/        # Prompt templates
│   └── graph/          # Workflow definitions
├── tests/              # Tests
└── config/             # Configuration files
```

## Development

1. Create virtual environment
2. Install development dependencies
3. Run tests

## License

MIT
