import json
import os

def extract_pre_res_data(directory: str, output_file: str):
    """
    从pre-res目录下提取数据并合并
    
    Args:
        directory: 源目录路径 (genehop 或 geneturing)
        output_file: 输出文件名
    """
    print(f"\n处理目录: {directory}")
    all_data = []
    
    # 读取目录下所有json文件
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            task_name = os.path.splitext(filename)[0]  # 获取不带后缀的文件名作为task名
            
            print(f"正在处理文件: {filename}")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # 处理每个问题-答案对
                for qa_item in data:
                    # qa_item 的格式是 [question, ground_truth, answer, prompts]
                    extracted_item = {
                        "task": task_name,
                        "question": qa_item[0],  # 第一个元素是问题
                        "ground_truth": qa_item[1],  # 第二个元素是标准答案
                        "answer": qa_item[2]  # 第三个元素是实际回答
                    }
                    all_data.append(extracted_item)
            
            except Exception as e:
                print(f"处理文件 {filename} 时出错: {str(e)}")
                continue
    
    # 保存合并后的数据
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    
    print(f"提取完成！结果已保存到: {output_file}")

def main():
    # 基础目录
    base_dir = ""
    
    # 处理 geneturing (9个文件)
    geneturing_dir = os.path.join(base_dir, "geneturing")
    extract_pre_res_data(
        geneturing_dir, 
        "pre_geneturing_result_extracted.json"
    )
    
    # 处理 genehop (3个文件)
    genehop_dir = os.path.join(base_dir, "genehop")
    extract_pre_res_data(
        genehop_dir, 
        "pre_genehop_result_extracted.json"
    )

if __name__ == "__main__":
    main()