import json
import re
from typing import Union, List, Dict, Tuple
import os
from dotenv import load_dotenv
import openai

class Evaluator:
    @staticmethod
    def normalize_text(text: str) -> str:
        """标准化文本，去除markdown格式和特殊字符"""
        # 去除markdown加粗符号
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        # 去除列表符号和换行
        text = re.sub(r'[\n\r]+[-•*]\s*', ' ', text)
        # 去除其他标点符号，保留连字符
        text = re.sub(r'[^\w\s\-\.]', ' ', text)
        # 转换为小写并去除多余空格
        return ' '.join(text.lower().split())

    @staticmethod
    def extract_chromosome(text: str) -> str:
        """提取染色体编号，支持多种格式"""
        # 标准化文本
        text = text.lower().replace('chromosome', 'chr')
        
        # 匹配模式：
        patterns = [
            r'chr\s*(\d+|x|y)',  # chr8, chr 8
            r'(\d+|x|y)[pq][\d\.]*',  # 8p23.1, 8p
            r'\b(\d+|x|y)\b(?=\s*(?:p|q|\s|$))'  # 单独的数字，后面跟着p/q或空格或结束
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                chr_num = match.group(1)
                return f"chr{chr_num}"
        
        return ""

    @staticmethod
    def chromosome_match(ground_truth: str, answer: str) -> float:
        """染色体位置匹配"""
        # 从ground truth和answer中提取染色体编号
        gt_chr = Evaluator.extract_chromosome(ground_truth)
        ans_chr = Evaluator.extract_chromosome(answer)
        return 1.0 if gt_chr and ans_chr and gt_chr == ans_chr else 0.0

    @staticmethod
    def string_match(ground_truth: str, answer: str) -> float:
        """字符串精确匹配"""
        normalized_answer = Evaluator.normalize_text(answer)
        normalized_gt = Evaluator.normalize_text(ground_truth)
        return 1.0 if normalized_gt in normalized_answer else 0.0
    
    @staticmethod
    def recall_score(ground_truth: List[str], answer: str) -> float:
        """计算召回率 (correct answers / ground-truth answers)"""
        normalized_answer = Evaluator.normalize_text(answer)
        normalized_gt = [Evaluator.normalize_text(gt) for gt in ground_truth]
        # 计算有多少个ground truth在答案中出现
        correct = sum(1 for gt in normalized_gt if gt in normalized_answer)
        return correct / len(ground_truth) if ground_truth else 0.0
    
    @staticmethod
    def extract_genomic_location(text: str) -> Tuple[str, str, str]:
        """
        从文本中提取基因组位置信息
        返回: (染色体编号, 起始位置, 结束位置)
        """
        text = text.lower()
        
        # 首先获取染色体编号
        chr_num = Evaluator.extract_chromosome(text)
        if not chr_num:
            return "", "", ""
        
        # 查找位置范围的不同模式
        patterns = [
            # 标准格式 chr15:91950805-91950932
            rf'{chr_num}:(\d+)-(\d+)',
            # 位置格式 position: 91950805 to 91950932
            r'position:?\s*(\d+)\s*(?:to|-)\s*(\d+)',
            # 位置格式 91950805-91950932
            r'(?<!\d)(\d{6,})\s*(?:to|-)\s*(\d{6,})(?!\d)',
            # 其他可能的位置格式...
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return chr_num, match.group(1), match.group(2)
        
        # 如果找到染色体但没找到位置，返回只有染色体的结果
        return chr_num, "", ""

    @staticmethod
    def dna_alignment_score(ground_truth: str, answer: str) -> float:
        """
        DNA比对评分
        1.0 - 染色体和位置都完全匹配
        0.5 - 只有染色体匹配
        0.0 - 染色体不匹配
        """
        # 从标准答案和回答中提取信息
        gt_chr, gt_start, gt_end = Evaluator.extract_genomic_location(ground_truth)
        
        # 首先检查染色体匹配
        ans_chr = Evaluator.extract_chromosome(answer)
        
        if not (gt_chr and ans_chr and gt_chr == ans_chr):
            return 0.0
        
        # 如果染色体匹配，继续查找位置信息
        ans_chr, ans_start, ans_end = Evaluator.extract_genomic_location(answer)
        # 如果找到了完全匹配的位置
        if gt_start and gt_end and ans_start and ans_end:
            if gt_start == ans_start and gt_end == ans_end:
                return 1.0
        
        # 如果只匹配到染色体
        return 0.5

class LLMEvaluator:
    def __init__(self):
        load_dotenv()
        self.client = openai.OpenAI(
            api_key='ollama',
            base_url="http://34.142.153.30:11434/v1/"  # Ollama 服务器地址
        )

    def evaluate_with_llm(self, task_type: str, question: str, ground_truth: Union[str, List[str]], answer: str) -> float:
        """使用LLM评估答案"""
        
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
            # 使用新的 OpenAI 调用方式
            response = self.client.chat.completions.create(
                model="qwen2.5:32b",  # 这里是正确的位置
                messages=[
                    {"role": "system", "content": "You are a biological evaluation expert. Evaluate the answer based on the given criteria and return only a numerical score."},
                    {"role": "user", "content": prompts[task_type]}
                ]
            )
            
            # 获取响应文本
            score_text = response.choices[0].message.content
            
            # 提取分数
            score = float(re.search(r'(\d+\.?\d*)', score_text).group(1))
            print(f"LLM评估得分: {score}")
            return min(max(score, 0.0), 1.0)  # 确保分数在0-1之间
            
        except Exception as e:
            print(f"LLM评估出错: {str(e)}")
            return 0.0

def evaluate_answer(task_type: str, question: str, ground_truth: Union[str, List[str]], answer: str) -> float:
    """根据任务类型选择评估方法"""
    
    # 只有这些复杂的任务需要 LLM 评估
    llm_tasks = {
        "SNP gene function",  # 基因功能描述需要语义理解
        "Multi-species DNA alignment",  # 物种识别可能需要上下文理解
        "Protein-coding genes"  # 蛋白质编码状态可能需要复杂判断
    }
    
    # 使用规则匹配的任务
    evaluator = Evaluator()
    
    if task_type in llm_tasks:
        llm_evaluator = LLMEvaluator()
        return llm_evaluator.evaluate_with_llm(task_type, question, ground_truth, answer)
    elif task_type == "Human genome DNA alignment":
        # DNA 比对位置匹配
        return evaluator.dna_alignment_score(ground_truth, answer)
    elif task_type in ["Gene location", "SNP location"]:
        # 染色体位置匹配
        return evaluator.chromosome_match(ground_truth, answer)
    elif task_type in ["Gene alias", "Gene name conversion", "Gene SNP association"]:
        # 精确字符串匹配
        return evaluator.string_match(ground_truth, answer)
    elif task_type in ["Gene disease association", "Disease gene location", "sequence gene alias"]:
        # 召回率计算
        if isinstance(ground_truth, str):
            ground_truth = [gt.strip() for gt in ground_truth.split(',')]
        return evaluator.recall_score(ground_truth, answer)
    
    return 0.0

def evaluate_results(input_file: str):
    """评估结果文件"""
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 初始化结果统计
    task_results: Dict[str, List[Dict]] = {}
    
    # LLM 评估的任务列表
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
        
        # 计算得分
        score = evaluate_answer(task_type, question, ground_truth, answer)
        
        # 为需要 LLM 评估的任务添加 (manual) 标记
        display_task_type = f"{task_type} (manual)" if task_type in llm_tasks else task_type
        
        # 保存结果，保持原有结构并添加得分
        if display_task_type not in task_results:
            task_results[display_task_type] = []
            
        result_item = {
            "question": question,
            "ground_truth": ground_truth,
            "answer": answer,
            "score": score
        }
        task_results[display_task_type].append(result_item)
    
    # 生成评估报告
    report = {
        "task_statistics": {},
        "overall_statistics": {
            "total_questions": 0,
            "total_score": 0.0,
            "questions_need_manual_review": 0
        }
    }
    
    # 计算每个任务的统计信息
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
        
        # 更新总体统计
        report["overall_statistics"]["total_questions"] += len(results)
        report["overall_statistics"]["total_score"] += sum(scores)
        report["overall_statistics"]["questions_need_manual_review"] += need_manual
    
    # 计算总体平均分
    total_evaluated = (report["overall_statistics"]["total_questions"] - 
                      report["overall_statistics"]["questions_need_manual_review"])
    if total_evaluated > 0:
        report["overall_statistics"]["average_score"] = (
            report["overall_statistics"]["total_score"] / total_evaluated
        )
    
    # 保存结果，格式更适合人工检查
    output_file = input_file.replace('.json', '_scored.json')
    output_data = {
        "results_by_task": task_results,  # 按任务类型组织的详细结果
        "statistics": report  # 统计信息
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    # 打印报告
    print(f"\n评估完成！结果已保存到: {output_file}")
    print("\n=== 任务类型统计 ===")
    for task_type, stats in report["task_statistics"].items():
        print(f"\n{task_type}:")  # task_type 已经包含了 (manual) 标记
        print(f"  总问题数: {stats['total_questions']}")
        print(f"  已评估数: {stats['evaluated_questions']}")
        print(f"  需人工评分: {stats['need_manual_review']}")
        print(f"  满分数量: {stats['perfect_score_count']}")
        print(f"  零分数量: {stats['zero_score_count']}")
        print(f"  部分得分: {stats['partial_score_count']}")
        print(f"  平均分: {stats['average_score']:.3f}")

    
    print("\n=== 总体统计 ===")
    print(f"总问题数: {report['overall_statistics']['total_questions']}")
    print(f"需人工评分数: {report['overall_statistics']['questions_need_manual_review']}")
    print(f"总体平均分: {report['overall_statistics'].get('average_score', 0):.3f}")

def main():
    # 处理所有结果文件
    result_files = [
        "pre_genehop_result_extracted.json",
        "pre_geneturing_result_extracted.json"
    ]
    
    for file in result_files:
        if os.path.exists(file):
            print(f"\n处理文件: {file}")
            evaluate_results(file)
        else:
            print(f"\n文件不存在: {file}")

if __name__ == "__main__":
    main()