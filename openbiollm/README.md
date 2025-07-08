# OpenBioLLM: Multi-Agent Architecture for Genomic Question Answering

A multi-agent RAG system based on LangChain and LangGraph for intelligent question answering in the field of bioinformatics.

## Features

- **Multi-Agent Collaborative System**: Specialized agents for different biomedical tasks
- **Intelligent Routing**: Automatic query classification and agent selection
- **NCBI Integration**: Direct access to E-utilities and BLAST databases
- **Web Search Capability**: Enhanced information retrieval for complex queries
- **Quality Evaluation**: Automatic assessment and iteration control
- **Comprehensive Evaluation**: Built-in evaluation framework for performance analysis

## Architecture

### Core Components

- **Router**: Intelligent query classification and agent routing
- **Evaluator**: Quality assessment and iteration control
- **Generator**: Final answer synthesis and formatting

### Specialized Agents

- **EUtils Agent**: NCBI database querying (genes, proteins, diseases)
- **BLAST Agent**: Biological sequence alignment and comparison
- **Search Agent**: Google Web search and information retrieval

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment variables
# Update the base_url in src/core/*.py files with your Ollama server URL
```

## Configuration

1. Update the following files with your Ollama server configuration:

- `src/core/router.py`
- `src/core/evaluator.py` 
- `src/core/generator.py`
- `src/agents/*/component.py`

Replace `base_url="xxxxxxxxxxxxxx"` with your actual Ollama server URL.

2. Update Google API key and Google Custom Search Engine ID in `src/agents/search_agent/component.py`

```python
    self.api_key = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'  # Replace with your actual API key
    self.cse_id = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'  # Replace with your actual Custom Search Engine ID
```

## Usage

### Batch Processing

Run the complete evaluation on GeneHop and GeneTuring datasets:

```bash
python main.py
```

This will process:
- `data/geneturing.json` → `results/geneturing_14b_14b_result.json`
- `data/genehop.json` → `results/genehop_14b_14b_result.json`

### Interactive Demo

Test individual questions interactively:

```bash
python main_demo.py
```

Edit the questions list in `main_demo.py` to test different queries.

### Evaluation

Extract and evaluate results:

```bash
python extract.py
python evaluate.py
```

## Project Structure

```
openbiollm/
├── src/                    # Source code
│   ├── agents/            # Agent implementations
│   │   ├── blast_agent/   # BLAST sequence alignment
│   │   ├── eutils_agent/  # NCBI E-utilities
│   │   └── search_agent/  # Web search
│   ├── core/              # Core system components
│   │   ├── rag.py         # Main RAG workflow
│   │   ├── router.py      # Query routing
│   │   ├── evaluator.py   # Quality evaluation
│   │   └── generator.py   # Answer generation
│   └── tools/             # Utility functions
├── data/                  # Datasets
│   ├── geneturing.json    # GeneTuring dataset
│   ├── genehop.json       # GeneHop dataset
│   └── *.json            # Other datasets
├── results/               # Output results
├── statistics/            # Plot generated
├── main.py               # Batch processing
├── main_demo.py          # Interactive demo
├── extract.py            # Result extraction
└── evaluate.py           # Evaluation framework
```

## Datasets

- **GeneTuring**: Gene function prediction tasks
  - Gene alias identification
  - Gene-disease association
  - Gene location queries
  - Sequence alignment
  - SNP analysis

- **GeneHop**: Gene-related question answering
  - Disease-gene location
  - Sequence gene alias
  - SNP gene function


## Results

Results are automatically saved to the `results/` directory with detailed execution traces including:
- Processing time
- Node-by-node execution flow
- Final answers
- Error handling

## Development

The system is built with:
- **LangChain**: Agent framework
- **LangGraph**: Multi-agent workflow
- **Ollama**: Local LLM management
- **NCBI APIs**: Biological database access

## License

MIT
