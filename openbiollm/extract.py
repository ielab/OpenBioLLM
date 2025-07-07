import json
import os

def extract_key_info(input_file: str):
    """Extract key information and save to new file"""
    # Read original file
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract key information
    extracted_data = []
    for item in data:
        extracted_item = {
            "task": item["task"],
            "question": item["question"],
            "ground_truth": item["ground_truth"],
            "answer": item["answer"]
        }
        extracted_data.append(extracted_item)
    
    # Generate new file name
    base_name = os.path.splitext(input_file)[0]
    output_file = f"{base_name}_extracted.json"
    
    # Save extracted data
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(extracted_data, f, indent=2, ensure_ascii=False)
    
    print(f"Extraction completed! Results saved to: {output_file}")


def main():
    # Process all result files
    result_files = [
        "results/geneturing_14b_14b-3_result.json",
        "results/genehop_14b_14b-3_result.json"
    ]
    
    for file in result_files:
        if os.path.exists(file):
            print(f"\nProcessing file: {file}")
            extract_key_info(file)
        else:
            print(f"\nFile not found: {file}")

if __name__ == "__main__":
    main()