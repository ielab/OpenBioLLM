import json
import csv

# Define all files and their corresponding column names
files_and_names = [
    # GeneTuring
    # ('results/pre_genegpt/pre_geneturing_result_extracted_scored.json', 'Score_pre_genegpt'),
    # ('results/pre_genegpt_slim/pre_geneturing_result_extracted_scored.json', 'Score_pre_genegpt_slim'),
    # ('results/pre_qwen32b/pre_geneturing_result_extracted_scored.json', 'Score_pre_qwen32b'),
    # ('results/pre_qwen72b/pre_geneturing_result_extracted_scored.json', 'Score_pre_qwen72b'),
    # ('results/multi_agent_14b_7b/geneturing_14b_7b_result_extracted_scored.json', 'Score_14b_7b'),
    # ('results/multi_agent_14b_14b/geneturing_14b_14b_result_extracted_scored.json', 'Score_14b_14b'),
    # ('results/multi_agent_32b_14b/geneturing_result_extracted_scored.json','Score_32b_14b'),
    # ('results/multi_agent_32b_32b/geneturing_32b_32b_result_extracted_scored.json','Score_32b_32b'),

    # GeneHop
    ('results/pre_genegpt/pre_genehop_result_extracted_scored.json', 'genegpt'),
    ('results/pre_qwen32b/pre_genehop_result_extracted_scored.json', 'qwen2.5:32b'),
    ('results/pre_qwen72b/pre_genehop_result_extracted_scored.json', 'qwen2.5:72b'),
    ('results/multi_agent_14b_7b/genehop_14b_7b-3_result_extracted_scored.json', 'multi-agent(14b+7b)'),
    ('results/multi_agent_14b_14b/genehop_14b_14b_result_extracted_scored.json', 'multi-agent(14b+14b)'),
    ('results/multi_agent_32b_14b/genehop_result_extracted_scored.json','multi-agent(32b+14b)'),
    ('results/multi_agent_32b_32b/genehop_32b_32b-2_result_extracted_scored.json','multi-agent(32b+32b)'),
]

def create_question_map(data):
    """Create a mapping from questions to scores"""
    question_map = {}
    for task_name, questions in data['results_by_task'].items():
        for q in questions:
            # Use task name and question content as unique identifier
            key = (task_name, q['question'])
            question_map[key] = q['score']
    return question_map

# Read all files and create question mappings
all_question_maps = {}
all_questions = set()  # For storing all unique questions
for file_path, _ in files_and_names:
    with open(file_path, 'r') as f:
        data = json.load(f)
        question_map = create_question_map(data)
        all_question_maps[file_path] = question_map
        # Collect all unique questions
        for task_name, questions in data['results_by_task'].items():
            for q in questions:
                all_questions.add((task_name, q['question']))

# Create CSV file
with open('comparison_output-2.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    
    # Build headers
    headers = ['TaskName', 'Question_Number', 'Question'] + [name for _, name in files_and_names]
    writer.writerow(headers)
    
    # Sort all questions by task name
    sorted_questions = sorted(list(all_questions))
    
    # Count questions for each task
    task_counters = {}
    
    # Iterate through all collected questions
    for task_name, question in sorted_questions:
        # Update question count for this task
        if task_name not in task_counters:
            task_counters[task_name] = 1
        question_num = task_counters[task_name]
        task_counters[task_name] += 1
        
        # Collect scores from all models
        scores = []
        for file_path, _ in files_and_names:
            score = all_question_maps[file_path].get((task_name, question), 'N/A')
            scores.append(score)
        
        # Write one row of data
        row = [
            task_name,
            f'Q{question_num}',
            question,
        ] + scores
        
        writer.writerow(row)