import json
import os
import logging
import time 
from src.core.settings import configure_settings
from src.core.rag import initialize_rag_system
from langchain_core.messages import HumanMessage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_questions(file_path: str) -> dict:
    """Load questions from JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_results(results: list, output_file: str):
    """Save results to JSON file"""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"Results saved to: {output_file}")

def main():
    configure_settings()
    workflow = initialize_rag_system()
    
    file_processing_configs = [
        {
            "input_file": "data/geneturing.json",
            "output_file": "results/geneturing_14b_14b-3_result.json"
        },
        {
            "input_file": "data/genehop.json",
            "output_file": "results/genehop_14b_14b-3_result.json"
        }
    ]
    
    for config in file_processing_configs:
        input_file = config["input_file"]
        output_file = config["output_file"]
        
        logger.info(f"Processing file: {input_file}")
        
        qas = load_questions(input_file)
        results = []
        
        if os.path.exists(output_file):
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    results = json.load(f)
                done_set = {(r['task'], r['question']) for r in results if 'task' in r and 'question' in r}
                logger.info(f"Loaded {len(results)} historical results from {output_file}.")
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse historical results file {output_file}. Will start over.")
                done_set = set()
                results = [] # Reset results to avoid appending to corrupted data
        else:
            done_set = set()
        
        print(f"\nProcessing {input_file}")
        print("="*50)
        
        for task, info in qas.items():
            for question, ground_truth in info.items():
                if (task, question) in done_set:
                    print(f"Skipping processed: [{task}] {question}")
                    continue
                
                print(f"\nTask type: {task}")
                print(f"Question: {question}")
                print(f"Ground truth: {ground_truth}")
                
                start_time = time.time() # Record the start time of question processing
                execution_trace = [] # Used to record node outputs in order
                
                try:
                    # Create input
                    inputs = {
                        "messages": [
                            HumanMessage(content=question, additional_kwargs={"type": "user_question"})
                        ]
                    }
                    
                    # Execute workflow and collect all outputs
                    for output_chunk in workflow.stream(inputs):
                        node_name = list(output_chunk.keys())[0]
                        node_output_value = output_chunk[node_name]
                        
                        current_content = ""
                        if isinstance(node_output_value, dict):
                            if "messages" in node_output_value and node_output_value["messages"]:
                                latest_message = node_output_value["messages"][-1]
                                if hasattr(latest_message, 'content'):
                                    current_content = latest_message.content
                                else:
                                    current_content = str(latest_message)
                            elif "thinking_content" in node_output_value.get("metadata", {}):
                                current_content = node_output_value["metadata"]["thinking_content"]
                            else:
                                current_content = str(node_output_value)
                        elif isinstance(node_output_value, list) and node_output_value:
                             latest_message = node_output_value[-1]
                             if hasattr(latest_message, 'content'):
                                 current_content = latest_message.content
                             else:
                                 current_content = str(latest_message)
                        else:
                            current_content = str(node_output_value)

                        execution_trace.append({
                            "node_name": node_name,
                            "output_content": current_content
                        })

                    end_time = time.time() # Record the end time of question processing
                    processing_time_seconds = round(end_time - start_time, 2) # Calculate processing time

                    final_answer_content = "No answer generated"
                    # Try to get the answer from the last output of the 'generate' node
                    # Or get the answer from the last output of the entire execution trace
                    generate_outputs = [trace["output_content"] for trace in execution_trace if trace["node_name"] == "generate" and trace["output_content"]]
                    if generate_outputs:
                        final_answer_content = generate_outputs[-1]
                    elif execution_trace and execution_trace[-1]["output_content"]: # Otherwise, get the output of the last node
                        final_answer_content = execution_trace[-1]["output_content"]
                    
                    # Save results
                    result = {
                        "task": task,
                        "question": question,
                        "ground_truth": ground_truth,
                        "answer": final_answer_content,
                        "processing_time_seconds": processing_time_seconds, # Add processing time
                        "execution_trace": execution_trace # Add node outputs in order
                    }
                    results.append(result)
                    
                    print(f"Answer: {final_answer_content}")
                    print(f"Processing time: {processing_time_seconds} seconds")
                    print("="*50)
                    
                    # Save results after each question is processed
                    save_results(results, output_file)
                    
                except Exception as e:
                    end_time = time.time() # Record time even if there is an error
                    processing_time_seconds = round(end_time - start_time, 2)
                    logger.error(f"Error processing question: {str(e)}", exc_info=True)
                    result = {
                        "task": task,
                        "question": question,
                        "ground_truth": ground_truth,
                        "answer": f"Error: {str(e)}",
                        "processing_time_seconds": processing_time_seconds,
                        "execution_trace": execution_trace # Keep the existing execution trace
                    }
                    results.append(result)
                    save_results(results, output_file)
                    print(f"Error processing question: {str(e)}")
                    print(f"Processing time: {processing_time_seconds} seconds")
                    print("="*50)
                    continue
        logger.info(f"Processing of {input_file} completed. Results saved to {output_file}")

if __name__ == "__main__":
    main()