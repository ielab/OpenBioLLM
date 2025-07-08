# OpenBioLLM: Multi-Agent Architecture for Genomic Question Answering

A multi-agent RAG system based on LangChain and LangGraph for intelligent question answering in the field of bioinformatics.

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

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
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
self.api_key = 'xxxxxxxxxxxxxxxxxx'  # Replace with your actual API key
self.cse_id = 'xxxxxxxxxxxxxxxxxxx'  # Replace with your actual Custom Search Engine ID
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

## Results

Results are automatically saved to the `results/` directory with detailed execution traces including:
- Processing time
- Node-by-node execution flow
- Final answers
- Error handling


## License

MIT
