import json
import csv

# Model file path and name
files_and_names = [
    # ('../results/multi_agent_14b_7b/geneturing_14b_7b_result.json', 'multi-agent(14b+7b)'),
    # ('../results/multi_agent_14b_14b/geneturing_14b_14b_result.json', 'multi-agent(14b+14b)'),
    # ('../results/multi_agent_32b_14b/geneturing_32b_14b-3_result.json', 'multi-agent(32b+14b)'),
    # ('../results/multi_agent_32b_32b/geneturing_32b_32b-3_result.json', 'multi-agent(32b+32b)'),

    ('../results/multi_agent_14b_7b/genehop_14b_7b_result.json', 'multi-agent(14b+7b)'),
    ('../results/multi_agent_14b_14b/genehop_14b_14b_result.json', 'multi-agent(14b+14b)'),
    ('../results/multi_agent_32b_14b/genehop_32b_14b-3_result.json', 'multi-agent(32b+14b)'),
    ('../results/multi_agent_32b_32b/genehop_32b_32b-3_result.json', 'multi-agent(32b+32b)')
]

# All questions set and round mapping
all_questions = set()
round_map_all = {}

# Generic function to get round count
def get_evaluator_round_count(q):
    # Case 1: Has node_outputs format (priority)
    try:
        return q["node_outputs"]["evaluator"]["metadata"]["eval_count"]
    except (KeyError, TypeError):
        pass

    # Case 2: Has execution_trace format
    try:
        return sum(1 for step in q["execution_trace"] if step.get("node_name") == "evaluator")
    except (KeyError, TypeError):
        pass

    # fallback
    return 0

# Iterate through all model files
for file_path, model_name in files_and_names:
    with open(file_path, 'r') as f:
        data = json.load(f)

    round_map = {}

    # Structure assumed to be list of questions
    if isinstance(data, list):
        for q in data:
            task = q.get('task', 'Unknown')
            question = q.get('question', '').strip()
            key = (task, question)
            all_questions.add(key)
            round_map[key] = get_evaluator_round_count(q)
    else:
        print(f"File format exception: {file_path}")
        continue

    round_map_all[model_name] = round_map

# Write to CSV
with open('round_count_comparison.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)

    # Headers
    headers = ['TaskName', 'Question_Number', 'Question'] + [name for _, name in files_and_names]
    writer.writerow(headers)

    # Sort & number
    sorted_questions = sorted(list(all_questions))
    task_counters = {}

    for task_name, question in sorted_questions:
        if task_name not in task_counters:
            task_counters[task_name] = 1
        question_num = task_counters[task_name]
        task_counters[task_name] += 1

        row = [task_name, f"Q{question_num}", question]
        for _, model_name in files_and_names:
            count = round_map_all.get(model_name, {}).get((task_name, question), 'N/A')
            row.append(count)
        writer.writerow(row)