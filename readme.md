# Beyond GeneGP: A Multi-Agent Architecture with Open-Source LLMs for Enhanced Genomic Question Answering

## Overview of *OpenBioLLM* Project 

This repository contains two main versions exploring and optimising large language model applications in the biomedical domain:

1. **Pilot Study**: A reproduction and improvement of GeneGPT settings using Ollama for open-source model management
2. **OpenBioLLM**: A novel multi-agent architecture system

## Project Structure

```
OpenBioLLM/
├── pilotstudy/          # Pilot Study - GeneGPT reproduction with Ollama
├──  openbiollm/         # OpenBioLLM - Multi-agent architecture
└── README.md            # README.md
```

## Version Details

### 1. Pilot Study (`pilotstudy/`)

**Objective**: Reproduce GeneGPT research settings using Ollama for open-source model management

**Key Features**:
- Based on original GeneGPT settings and evaluation methods
- Uses Ollama for unified management of various open-source LLMs
- Includes prompt engineering optimized versions
- Supports multiple model comparison experiments (Qwen2.5-32B, Qwen2.5-72B, Llama3.1-70B, etc.)


**Experimental Settings**:
- Original setting reproduction
- Prompt engineering optimized versions (`-optimized`)
- Full version vs. slim version comparisons
- Multi-step reasoning experiments

**Models Tested**:
- Qwen2.5-32B, Qwen2.5-72B
- Llama3.1-70B
- Qwen2.5-coder-32B

### 2. OpenBioLLM (`openbiollm/`)

**Objective**: Build a novel multi-agent architecture system for enhanced genomic question answering

**Technology Stack**:
- **LangChain**: Agent framework
- **LangGraph**: Multi-agent collaboration
- **Multi-Agent Architecture**: Specialized agent division of labor

**Core Components**:
- **Router**: Intelligent routing system for query classification
- **Evaluator**: Quality assessment and iteration control
- **Generator**: Final answer synthesis

- **Search Agent**: Web search and information retrieval
- **BLAST Agent**: Biological sequence alignment and comparison
- **EUtils Agent**: NCBI database querying (genes, proteins, diseases)


**Architecture Advantages**:
- Modular design for easy extension
- Specialized agent division of labor
- Configurable collaboration strategies
- Automatic evaluation script

## Quick Start

### Pilot Study Version

```bash
cd pilotstudy/
# See README.md for detailed setup and running instructions
```

### OpenBioLLM Version

```bash
cd openbiollm/
# See README.md for detailed setup and running instructions
```

## Datasets

- **GeneHop**: Contains gene alias, disease-gene location, and SNP gene function tasks
- **GeneTuring**: Includes gene alias, gene-disease association, and gene location tasks

## Citation

If you use this work in your research, please cite our paper:

```bibtex
pending
```

## Contributing

We welcome contributions! Please feel free to submit issues and pull requests.

## License
```bibtex
pending
```
