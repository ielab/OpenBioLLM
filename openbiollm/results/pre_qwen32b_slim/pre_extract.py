import json
import os

def extract_pre_res_data(directory: str, output_file: str):
    """
    Extract data from pre-res directory and merge
    
    Args:
        directory: Source directory path (genehop or geneturing)
        output_file: Output file name
    """
    print(f"\nProcessing directory: {directory}")
    all_data = []
    
    # Read all json files in the directory
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            task_name = os.path.splitext(filename)[0]  # Get file name without extension as task name
            
            print(f"Processing file: {filename}")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Process each question-answer pair
                for qa_item in data:
                    # qa_item format is [question, ground_truth, answer, prompts]
                    extracted_item = {
                        "task": task_name,
                        "question": qa_item[0],  # First element is question
                        "ground_truth": qa_item[1],  # Second element is standard answer
                        "answer": qa_item[2]  # Third element is actual answer
                    }
                    all_data.append(extracted_item)
            
            except Exception as e:
                print(f"Error processing file {filename}: {str(e)}")
                continue
    
    # Save merged data
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    
    print(f"Extraction completed! Results saved to: {output_file}")

def main():
    # Base directory
    base_dir = ""
    
    # Process geneturing (9 files)
    geneturing_dir = os.path.join(base_dir, "geneturing")
    extract_pre_res_data(
        geneturing_dir, 
        "pre_geneturing_result_extracted.json"
    )
    
    # Process genehop (3 files)
    genehop_dir = os.path.join(base_dir, "genehop")
    extract_pre_res_data(
        genehop_dir, 
        "pre_genehop_result_extracted.json"
    )

if __name__ == "__main__":
    main()