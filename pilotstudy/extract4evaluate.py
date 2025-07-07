import argparse
import json
import os

# Parsing command line arguments
parser = argparse.ArgumentParser(description="Extract relevant data from JSON files")
parser.add_argument('--input-dir', type=str, required=True, help="Root directory to recursively search for JSON files")
args = parser.parse_args()
input_dir = args.input_dir

# Read JSON file
def load_json_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        print(f"*** Failed to parse JSON file: {file_path}, Error: {e}")
        return None
    except Exception as e:
        print(f"*** Unexpected error while loading JSON: {file_path}, Error: {e}")
        return None

# Extract relevant data from JSON content
def extract_relevant_data(data):
    extracted_data = []
    for entry in data:
        if isinstance(entry, list) and len(entry) >= 3:
            twist2 = entry[1]  # Extraction of ground truth
            answer = entry[2]  # Extract the answer

            extracted_data.append({
                "ground_truth": twist2,
                "answer": answer
            })
        else:
            print(f"*** Skipping invalid data entry: {entry}")

    return extracted_data

# Recursively find all JSON files in the directory
def get_all_json_files(root_dir):
    json_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for file in filenames:
            if file.endswith('.json'):
                json_files.append(os.path.join(dirpath, file))
    return json_files

def main():
    # Validate input directory
    if not os.path.isdir(input_dir):
        print(f"*** Input directory does not exist: {input_dir}")
        return

    parent_dir = os.path.dirname(input_dir)
    output_directory = os.path.join(parent_dir, "extracted")

    # Create output directory if it doesn't exist
    if not os.path.exists(output_directory):
        print(f"Creating output directory: {output_directory}")
        os.makedirs(output_directory)

    # Get all JSON files from all subdirectories
    json_files = get_all_json_files(input_dir)

    if not json_files:
        print(f"*** No JSON files found in {input_dir}")
        return

    print(f"Found {len(json_files)} JSON files to process.")

    # Success and failure counters
    success_count = 0
    failure_count = 0

    for json_file_path in json_files:
        json_file_name = os.path.basename(json_file_path)
        print(f"Processing file: {json_file_name}")

        # Load JSON file data
        data = load_json_file(json_file_path)
        if data is None:
            print(f"*** Skipping file due to JSON load failure: {json_file_path}")
            failure_count += 1
            continue

        # Extract data
        filtered_data = extract_relevant_data(data)

        # Define output file path
        relative_path = os.path.relpath(json_file_path, input_dir)  # Preserve subdirectory structure
        output_file_path = os.path.join(output_directory, relative_path)
        output_dir = os.path.dirname(output_file_path)

        # Create subdirectories in extracted folder if necessary
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        output_file_path = output_file_path.replace('.json', '_extracted.json')

        # Check if the target file already exists
        if os.path.exists(output_file_path):
            print(f"File already exists, skipping: {output_file_path}")
            continue

        try:
            # Write extracted data to new JSON file
            with open(output_file_path, 'w', encoding='utf-8') as json_output_file:
                json.dump(filtered_data, json_output_file, ensure_ascii=False, indent=4)

            print(f"Data successfully written to {output_file_path}")
            success_count += 1

        except Exception as e:
            print(f"❗️❗️❗️ Failed to write file: {output_file_path}, Error: {e}")
            failure_count += 1

    # Summary report
    print("\n=== Summary ===")
    print(f"✅ Successfully processed files: {success_count}")
    print(f"❌ Failed files: {failure_count}")
    print("================")

if __name__ == '__main__':
    main()
