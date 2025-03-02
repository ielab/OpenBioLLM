# OpenBioLLM

## 1. Configuration
Install required dependencies

```shell
pip install -r requirements.txt
```

Open `main.py` and replace the placeholder with your own Ollama server URL:

```python
# Initialize the Ollama LLM client
llm = Ollama(
    model=model_name,
    base_url="http://xx.xxx.xxx.xx:xxxx",  # Replace with your own Ollama server URL
    temperature=0.0,
    request_timeout=500,
    context_window=16000,
)
```

## 2. Running Tests
Navigate to the `shell` directory, which contains the following test scripts:

- Run `geneturing.sh` to execute the **GeneTuring** test and generate results.
- Run `genehop.sh` to execute the **GeneHop** test and generate results.

All test results will be stored in the `res` directory.

## 3. Evaluation
To facilitate result evaluation, execute the `extract4evaluate.sh` script. This script will:

1. Create a new `extract` folder, extract all the json files in `res`, and keep the directory structure consistent with the entire `res` folder.
2. Generate `_extracted` versions of the output files, containing **ground truth labels** and **model answers** for side-by-side comparison and in-depth analysis.

