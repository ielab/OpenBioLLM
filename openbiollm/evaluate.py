import json
import re
from typing import Union, List, Dict, Tuple
import os
from dotenv import load_dotenv
import openai

class Evaluator:
    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalize text, remove markdown formatting and special characters"""
        # Remove markdown bold formatting
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        # Remove list symbols and newlines
        text = re.sub(r'[\n\r]+[-•*]\s*', ' ', text)
        # Remove other punctuation, keep hyphens
        text = re.sub(r'[^\w\s\-\.]', ' ', text)
        # Convert to lowercase and remove extra spaces
        return ' '.join(text.lower().split())

    @staticmethod
    def extract_chromosome(text: str) -> str:
        """Extract chromosome number, support multiple formats"""
        # Normalize text
        text = text.lower().replace('chromosome', 'chr')
        
        # Match patterns:
        patterns = [
            r'chr\s*(\d+|x|y)',  # chr8, chr 8
            r'(\d+|x|y)[pq][\d\.]*',  # 8p23.1, 8p
            r'\b(\d+|x|y)\b(?=\s*(?:p|q|\s|$))'  # Single number followed by p/q or space or end
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                chr_num = match.group(1)
                return f"chr{chr_num}"
        
        return ""

    @staticmethod
    def chromosome_match(ground_truth: str, answer: str) -> float:
        """Chromosome location matching"""
        # Extract chromosome number from ground truth and answer
        gt_chr = Evaluator.extract_chromosome(ground_truth)
        ans_chr = Evaluator.extract_chromosome(answer)
        return 1.0 if gt_chr and ans_chr and gt_chr == ans_chr else 0.0

    @staticmethod
    def string_match(ground_truth: str, answer: str) -> float:
        """String exact match"""
        normalized_answer = Evaluator.normalize_text(answer)
        normalized_gt = Evaluator.normalize_text(ground_truth)
        return 1.0 if normalized_gt in normalized_answer else 0.0
    
    @staticmethod
    def recall_score(ground_truth: List[str], answer: str) -> float:
        """Calculate recall (correct answers / ground-truth answers)"""
        normalized_answer = Evaluator.normalize_text(answer)
        normalized_gt = [Evaluator.normalize_text(gt) for gt in ground_truth]
        # Calculate how many ground truths appear in the answer
        correct = sum(1 for gt in normalized_gt if gt in normalized_answer)
        return correct / len(ground_truth) if ground_truth else 0.0
    
    @staticmethod
    def extract_genomic_location(text: str) -> Tuple[str, str, str]:
        """
        Extract genomic location information from text
        Return: (chromosome number, start position, end position)
        """
        text = text.lower()
        
        # First get the chromosome number
        chr_num = Evaluator.extract_chromosome(text)
        if not chr_num:
            return "", "", ""
        
        # Find different patterns for location ranges
        patterns = [
            # Standard format chr15:91950805-91950932
            rf'{chr_num}:(\d+)-(\d+)',
            # Position format position: 91950805 to 91950932
            r'position:?\s*(\d+)\s*(?:to|-)\s*(\d+)',
            # Position format 91950805-91950932
            r'(?<!\d)(\d{6,})\s*(?:to|-)\s*(\d{6,})(?!\d)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return chr_num, match.group(1), match.group(2)
        
        # If a chromosome is found but no position is found, return only the chromosome
        return chr_num, "", ""

    @staticmethod
    def dna_alignment_score(ground_truth: str, answer: str) -> float:
        """
        DNA alignment score
        1.0 - Both chromosome and position match completely
        0.5 - Only chromosome matches
        0.0 - Chromosome does not match
        """
        # Extract information from standard answer and answer
        gt_chr, gt_start, gt_end = Evaluator.extract_genomic_location(ground_truth)
        
        # First check chromosome match
        ans_chr = Evaluator.extract_chromosome(answer)
        
        if not (gt_chr and ans_chr and gt_chr == ans_chr):
            return 0.0
        
        # If chromosome matches, continue to find position information
        ans_chr, ans_start, ans_end = Evaluator.extract_genomic_location(answer)
        # If a completely matching position is found
        if gt_start and gt_end and ans_start and ans_end:
            if gt_start == ans_start and gt_end == ans_end:
                return 1.0
        
        # If only chromosome matches, continue to find position information
        return 0.5

class LLMEvaluator:
    def __init__(self):
        load_dotenv()
        self.client = openai.OpenAI(
            api_key='ollama',
            base_url="http://34.142.153.30:11434/v1/"  # Ollama server address
        )

    def evaluate_with_llm(self, task_type: str, question: str, ground_truth: Union[str, List[str]], answer: str) -> float:
        """Evaluate answer with LLM"""
        
        prompts = {
            "Multi-species DNA alignment": f"""Task: Evaluate if the species identification in the answer matches the ground truth.
Question: {question}
Ground Truth: {ground_truth}
Answer: {answer}

Evaluation criteria:
1.0 - Correct species identification (Human equals to Homo sapiens, Chicken equals to Meleagris gallopavo or Turkey, etc.)
0.0 - Wrong species

For example:

"question": "Which organism does the DNA sequence come from:CATGTACAATAAAAGAACTGGAGGTATCACCTTCCCTGATTTCAAGCTGTAGTACAAAGCATTGTAACAAAAACATGCATGATATTGGCATAACAAGGACAGGTTGATCAATGGAATTGAGTTGAAGACCCAGAAATACACCCA",
"ground_truth": "rat",
"answer": "The DNA sequence provided comes from Mus musculus (mouse). The BLAST results show significant matches with various mouse genomic sequences and BAC clones, indicating that this sequence is of murine origin.",
"score": 1.0 (because mouse is rat)

"question": "Which organism does the DNA sequence come from:CATGCAATGAGATTGCTGCACACCAGGAACCCTAACTTCCAGTCTTTTGTTTTCTGCTTGTAGCATGCTTGTTTTCTACACACTGTCATGGGTGTATGCAGATAAAAATAATCAATCCACGAC",
"ground_truth": "chicken",
"answer": "The DNA sequence most likely comes from the red-legged partridge (*Alectoris rufa*), as it shows a high identity (93%) with a segment of its genome assembly on chromosome 13. The second best match is with the wild turkey (*Meleagris gallopavo*), but with lower identity (89%).",
"score": 1.0 (because red-legged partridge can belong to chicken)


Return only a score (1.0 or 0.0)""",

            "Protein-coding genes": f"""Task: Evaluate if the protein-coding status in the answer matches the ground truth.
Question: {question}
Ground Truth: {ground_truth}
Answer: {answer}

Evaluation criteria:
1.0 - Correct identification (TRUE or YES for protein-coding, NA or NO or FALSE for non-protein-coding)
0.0 - Wrong identification

For example:
"question": "Is RPL7AP58 a protein-coding gene?",
"ground_truth": "NA",
"answer": "RPL7AP58 is not a protein-coding gene; it is a ribosomal protein L7a pseudogene 58.",
"score": 1.0 (because it mentions this is not a protein-coding gene)

Return only a score (1.0 or 0.0)""",

            "SNP gene function": f"""Task: Evaluate if the gene function description in the answer matches the ground truth.
Question: {question}
Ground Truth: {ground_truth}
Answer: {answer}

Evaluation criteria:
1.0 - Complete and accurate function description(exact match or non-coding gene is correctly mentioned)
0.5 - Partially correct description
0.0 - Wrong or irrelevant description

Return only a score (1.0, 0.5, or 0.0)"""
        }

        if task_type not in prompts:
            return 0.0

        try:
            response = self.client.chat.completions.create(
                model="qwen2.5:32b",
                messages=[
                    {"role": "system", "content": "You are a biological evaluation expert. Evaluate the answer based on the given criteria and return only a numerical score."},
                    {"role": "user", "content": prompts[task_type]}
                ]
            )
            
            # Get response text
            score_text = response.choices[0].message.content
            
            # Extract score
            score = float(re.search(r'(\d+\.?\d*)', score_text).group(1))
            print(f"LLM score: {score}")
            return min(max(score, 0.0), 1.0)  # Ensure score is between 0 and 1
            
        except Exception as e:
            print(f"LLM error: {str(e)}")
            return 0.0

def evaluate_answer(task_type: str, question: str, ground_truth: Union[str, List[str]], answer: str) -> float:
    """Select evaluation method based on task type"""
    
    # Only these complex tasks need LLM evaluation
    llm_tasks = {
        "SNP gene function", 
        "Multi-species DNA alignment",  
        "Protein-coding genes"  
    }
    
    # Tasks using rule matching
    evaluator = Evaluator()
    
    if task_type in llm_tasks:
        llm_evaluator = LLMEvaluator()
        return llm_evaluator.evaluate_with_llm(task_type, question, ground_truth, answer)
    elif task_type == "Human genome DNA alignment":
        # DNA alignment position matching
        return evaluator.dna_alignment_score(ground_truth, answer)
    elif task_type in ["Gene location", "SNP location"]:
        # Chromosome location matching
        return evaluator.chromosome_match(ground_truth, answer)
    elif task_type in ["Gene alias", "Gene name conversion", "Gene SNP association"]:
        # Exact string matching
        return evaluator.string_match(ground_truth, answer)
    elif task_type in ["Gene disease association", "Disease gene location", "sequence gene alias"]:
        # Recall calculation
        if isinstance(ground_truth, str):
            ground_truth = [gt.strip() for gt in ground_truth.split(',')]
        return evaluator.recall_score(ground_truth, answer)
    
    return 0.0

def evaluate_results(input_file: str):
    """Evaluate result file"""
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Initialize result statistics
    task_results: Dict[str, List[Dict]] = {}
    
    # LLM evaluation tasks
    llm_tasks = {
        "SNP gene function",
        "Multi-species DNA alignment",
        "Protein-coding genes"
    }
    
    for item in data:
        task_type = item['task']
        question = item['question']
        ground_truth = item['ground_truth']
        answer = item['answer']
        
        # Calculate score
        score = evaluate_answer(task_type, question, ground_truth, answer)
        
        # Add (manual) mark for tasks that need LLM evaluation
        display_task_type = f"{task_type} (manual)" if task_type in llm_tasks else task_type
        
        # Save results, keep original structure and add score
        if display_task_type not in task_results:
            task_results[display_task_type] = []
            
        result_item = {
            "question": question,
            "ground_truth": ground_truth,
            "answer": answer,
            "score": score
        }
        task_results[display_task_type].append(result_item)
    
    # Generate evaluation report
    report = {
        "task_statistics": {},
        "overall_statistics": {
            "total_questions": 0,
            "total_score": 0.0,
            "questions_need_manual_review": 0
        }
    }
    
    # Calculate statistics for each task
    for task_type, results in task_results.items():
        scores = [r["score"] for r in results if r["score"] >= 0]
        need_manual = sum(1 for r in results if r["score"] < 0)
        
        task_stats = {
            "total_questions": len(results),
            "evaluated_questions": len(scores),
            "need_manual_review": need_manual,
            "perfect_score_count": sum(1 for r in results if r["score"] == 1.0),
            "zero_score_count": sum(1 for r in results if r["score"] == 0.0),
            "partial_score_count": sum(1 for r in results if 0.0 < r["score"] < 1.0),
            "average_score": sum(scores) / len(scores) if scores else 0.0
        }
        
        report["task_statistics"][task_type] = task_stats
        
        # Update overall statistics
        report["overall_statistics"]["total_questions"] += len(results)
        report["overall_statistics"]["total_score"] += sum(scores)
        report["overall_statistics"]["questions_need_manual_review"] += need_manual
    
    # Calculate overall average score
    total_evaluated = (report["overall_statistics"]["total_questions"] - 
                      report["overall_statistics"]["questions_need_manual_review"])
    if total_evaluated > 0:
        report["overall_statistics"]["average_score"] = (
            report["overall_statistics"]["total_score"] / total_evaluated
        )
    
    output_file = input_file.replace('.json', '_scored.json')
    output_data = {
        "results_by_task": task_results,  # Organized by task type
        "statistics": report  # Statistics
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    # Print report
    print(f"\nEvaluation completed! Results saved to: {output_file}")
    print("\n=== Task type statistics ===")
    for task_type, stats in report["task_statistics"].items():
        print(f"\n{task_type}:")  # task_type already includes (manual) mark
        print(f"  Total questions: {stats['total_questions']}")
        print(f"  Evaluated questions: {stats['evaluated_questions']}")
        print(f"  Need manual review: {stats['need_manual_review']}")
        print(f"  Perfect score count: {stats['perfect_score_count']}")
        print(f"  Zero score count: {stats['zero_score_count']}")
        print(f"  Partial score count: {stats['partial_score_count']}")
        print(f"  Average score: {stats['average_score']:.3f}")

    
    print("\n=== Overall statistics ===")
    print(f"Total questions: {report['overall_statistics']['total_questions']}")
    print(f"Need manual review: {report['overall_statistics']['questions_need_manual_review']}")
    print(f"Overall average score: {report['overall_statistics'].get('average_score', 0):.3f}")

def main():
    # Process all result files
    result_files = [
        "results/geneturing_14b_14b-3_result_extracted.json",
        "results/genehop_14b_14b-3_result_extracted.json"
    ]
    
    for file in result_files:
        if os.path.exists(file):
            print(f"\nProcessing file: {file}")
            evaluate_results(file)
        else:
            print(f"\nFile not found: {file}")

if __name__ == "__main__":
    main()