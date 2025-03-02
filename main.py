import json
import os
import re
import logging
import time
import urllib.request
import argparse
from llama_index.llms.ollama import Ollama
from llama_index.core.llms import ChatMessage


# Parsing command line arguments
parser = argparse.ArgumentParser(description="Run GeneGPT")
parser.add_argument('mask', type=str, help="The mask string (e.g., '111111')")
parser.add_argument('--model', type=str, default= None, help="Model name")
parser.add_argument('--input', type=str, default= None, help="Input JSON file")
parser.add_argument('--results-dir', type=str, default = None, help="Directory for results")
parser.add_argument('--log-file', type=str, default= None, help="Log file name")
args = parser.parse_args()

str_mask = args.mask
model_name = args.model
input_file = args.input
results_dir = args.results_dir
log_filename = args.log_file

print(f"Using model: {model_name}")
print(f"Mask: {str_mask}")
print(f"Input file: {input_file}")
print(f"Results directory: {results_dir}")
print(f"Log file: {log_filename}")



# Set up logging
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.basicConfig(filename=log_filename, filemode='w', level=logging.DEBUG,
					format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()


# Initialize the Ollama LLM client
llm = Ollama(
	model=model_name,
	base_url="http://xx.xxx.xxx.xx:xxxx", # use your own ollama url
	temperature=0.0,
	request_timeout=500,
	context_window=16000,
)

def call_ollama(q_prompt,num_calls):
	logger.debug(f"---------------------------------No.{num_calls+1} Calling Ollama with prompt:---------------------------------\n{q_prompt}")
	try:
		messages = [
			ChatMessage(
				role="system", content="You are Qwen2.5, created by Alibaba Cloud. You are a helpful assistant."
			),
			ChatMessage(role="user", content= q_prompt),
		]
		response = llm.stream_chat(messages)
		result = "".join(r.delta for r in response)
		logger.info(f"---------------------------------No.{num_calls+1} LLM Generated Text:--------------------------------- \n {result}")
		print(f"---------------------------------No.{num_calls+1} LLM Generated Text:--------------------------------- \n {result}")
		return result
	except Exception as e:
		logger.error(f"Error calling Ollama with prompt: {q_prompt}")
		logger.error(f"Exception: {str(e)}", exc_info=True)
		return "Error"

def call_summary(html,num_calls):
	logger.debug(f"---------------------------------No.{num_calls+1} Calling Summary with prompt:---------------------------------\n{html}")
	s_prompt = f'Here is the a response from a http request, please help me extract important information, in order to better find the key point. Here are the response:\n{html}.\n Please list the key point.\n'

	try:
		messages = [
			ChatMessage(
				role="system", content="You are OpenBioLLM-70B, a State-of-the-Art Open Source Biomedical Large Language Model. You are a helpful assistant."
			),
			ChatMessage(role="user", content= s_prompt),
		]
		response = llm.stream_chat(messages)
		result = "".join(r.delta for r in response)
		logger.info(f"---------------------------------No.{num_calls+1} LLM Summary Text:---------------------------------\n {result}")
		print(f"---------------------------------No.{num_calls+1} LLM Summary Text:---------------------------------\n {result}")
		return result
	except Exception as e:
		logger.error(f"Exception: {str(e)}", exc_info=True)
		return "Error"


def call_api(url, max_retries=3):
	retry_count = 0
	time.sleep(1)
	url = url.replace(' ', '+')

	while retry_count < max_retries:
		try:
			logger.info(f"Calling API with URL: {url}")
			req = urllib.request.Request(url)
			with urllib.request.urlopen(req) as response:
				call = response.read()
			return call
		except urllib.error.HTTPError as e:
			if e.code == 500:
				retry_count += 1
				logger.warning(f"HTTP 500 Error encountered. Retry {retry_count}/{max_retries}...")
				time.sleep(5)
			else:
				logger.error(f"Error calling API with URL: {url}")
				logger.error(f"Exception: {str(e)}", exc_info=True)
				return None
		except Exception as e:
			logger.error(f"Error calling API with URL: {url}")
			logger.error(f"Exception: {str(e)}", exc_info=True)
			return None

	logger.error(f"API call failed after {max_retries} attempts.")
	return None

def get_prompt_header(mask):
	'''
    mask: [1/0 x 6], denotes whether each prompt component is used
    output: prompt
    '''
	url_1 = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gene&retmax=5&retmode=json&sort=relevance&term=LMP10'
	call_1 = call_api(url_1)

	url_2 = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=gene&retmax=5&retmode=json&sort=relevance&id=19171,5699,8138'
	call_2 = call_api(url_2)

	url_3 = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=snp&retmax=10&retmode=json&sort=relevance&id=1217074595'
	call_3 = call_api(url_3)

	url_4 = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=omim&retmax=20&retmode=json&sort=relevance&term=Meesmann+corneal+dystrophy'
	call_4 = call_api(url_4)

	url_5 = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=omim&retmax=20&retmode=json&sort=relevance&id=618767,601687,300778,148043,122100'
	call_5 = call_api(url_5)

	url_6 = 'https://blast.ncbi.nlm.nih.gov/blast/Blast.cgi?CMD=Put&PROGRAM=blastn&MEGABLAST=on&DATABASE=nt&FORMAT_TYPE=XML&QUERY=ATTCTGCCTTTAGTAATTTGATGACAGAGACTTCTTGGGAACCACAGCCAGGGAGCCACCCTTTACTCCACCAACAGGTGGCTTATATCCAATCTGAGAAAGAAAGAAAAAAAAAAAAGTATTTCTCT&HITLIST_SIZE=5'
	call_6 = call_api(url_6)
	rid = re.search('RID = (.*)\n', call_6.decode('utf-8')).group(1)

	url_7 = f'https://blast.ncbi.nlm.nih.gov/blast/Blast.cgi?CMD=Get&FORMAT_TYPE=Text&RID={rid}'
	time.sleep(30)
	call_7 = call_api(url_7)

	url_8 = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=omim&retmax=5&retmode=json&sort=relevance&term=Glycine+N-methyltransferase+deficiency'
	call_8 = call_api(url_8)
	response8 = '''{...,idlist":["606664","606628","601240","160993"],...}'''

	url_9 = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=omim&retmax=5&retmode=json&sort=relevance&id=606664,606628,601240,160993'
	call_9 = call_api(url_9)
	response9 = '''{...,"result":"606664":{...,"title":"GLYCINE N-METHYLTRANSFERASE DEFICIENCY",...},"606628":{...,"title":"GLYCINE N-METHYLTRANSFERASE; GNMT",...},"601240":{...,"title":"GUANIDINOACETATE METHYLTRANSFERASE; GAMT",...},...}'''

	url_10 = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gene&retmax=5&retmode=json&sort=relevance&term=GNMT'
	call_10 = call_api(url_10)
	response10 = '''{...,"esearchresult":{...,"idlist":["27232","14711","25134","41561","403338","697722"],...},...}'''

	url_11 = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=gene&retmax=5&retmode=json&sort=relevance&id=27232,14711,25134,41561,403338'
	call_11 = call_api(url_11)
	response11 = '''{...,"result":{...,"27232":{...,"uid":"27232","name":"GNMT","maplocation":"6p21.1",...},...}'''


	prompt = ''
	prompt += 'Hello. Your task is to use NCBI Web APIs to answer genomic questions.\n'
	prompt += 'Your response must always be in one of the following two formats:\n'

	prompt +='1. When you need to make an API call, please put the URL you generated directly in [], Do not add anything else.\n'
	prompt +='2. When you reach the final answer, Please use the following format：Answer: your generated answer.\n'

	if mask[0]:
		# Doc 0 is about Eutils
		prompt += 'You can call Eutils by: "[https://eutils.ncbi.nlm.nih.gov/entrez/eutils/{esearch|efetch|esummary}.fcgi?retmax=10&db={gene|snp|omim}&retmode=json&sort=relevance&{term|id}={term|id}]".\n'
		prompt += 'esearch: input is a search term and output is database id(s).\n'
		prompt += 'efectch/esummary: input is database id(s) and output is full records or summaries that contain name, chromosome location, and other information.\n'
		prompt += 'Normally, you need to first call esearch to get the database id(s) of the search term, and then call efectch/esummary to get the information with the database id(s).\n'
		prompt += 'Database: gene is for genes, snp is for SNPs, and omim is for genetic diseases.\n\n'

	if mask[1]:
		# Doc 1 is about BLAST
		prompt += 'For DNA sequences, you can use BLAST by: "[https://blast.ncbi.nlm.nih.gov/blast/Blast.cgi?CMD={Put|Get}&PROGRAM=blastn&MEGABLAST=on&DATABASE=nt&FORMAT_TYPE={XML|Text}&QUERY={sequence}&HITLIST_SIZE={max_hit_size}]".\n'
		prompt += 'BLAST maps a specific DNA {sequence} to its chromosome location among different species.\n'
		prompt += 'You need to first PUT the BLAST request and then GET the results using the RID returned by PUT.\n\n'

	if any(mask[2:]):
		prompt += 'Here are some examples:\n\n'

	if mask[2]:
		# Example 1 is from gene alias task
		prompt += f'Question: What is the official gene symbol of LMP10?\n'
		prompt += f'[{url_1}]->[{call_1}]\n'
		prompt += f'[{url_2}]->[{call_2}]\n'
		prompt += f'Answer: PSMB10\n\n'

	if mask[3]:
		# Example 2 is from SNP gene task
		prompt += f'Question: Which gene is SNP rs1217074595 associated with?\n'
		prompt += f'[{url_3}]->[{call_3}]\n'
		prompt += f'Answer: LINC01270\n\n'

	if mask[4]:
		# Example 3 is from gene disease association
		prompt += f'Question: What are genes related to Meesmann corneal dystrophy?\n'
		prompt += f'[{url_4}]->[{call_4}]\n'
		prompt += f'[{url_5}]->[{call_5}]\n'
		prompt += f'Answer: KRT12, KRT3\n\n'

	if mask[5]:
		# Example 4 is for BLAST
		prompt += f'Question: Align the DNA sequence to the human genome:ATTCTGCCTTTAGTAATTTGATGACAGAGACTTCTTGGGAACCACAGCCAGGGAGCCACCCTTTACTCCACCAACAGGTGGCTTATATCCAATCTGAGAAAGAAAGAAAAAAAAAAAAGTATTTCTCT\n'
		prompt += f'[{url_6}]->[{rid}]\n'
		prompt += f'[{url_7}]->[{call_7}]\n'
		prompt += f'Answer: chr15:91950805-91950932\n\n'


#  GeneHop multi-step reasoning
	if len(mask) > 6 and mask [6]:
		# Example 5 is for Disease gene location
		prompt += f'Question:List chromosome locations of the genes related to Hemolytic anemia due to phosphofructokinase deficiency. Let us decompose the question to sub-questions and solve them step by step:\n'
		prompt += f'Sub-question 1: What is the OMIM id of Glycine N-methyltransferase deficiency?\n'
		prompt += f'[{url_8}]->[{response8}]\n'
		prompt += f'Task 1: Extract the OMIM id in the list:[606664,606628,601240,160993]. Sub-question 2: What are genes related to OMIM id 606664,606628,601240,160993?\n'
		prompt += f'[{url_9}]->[{response9}]\n'
		prompt += f'Task 2: Extract Gene id of GNMT. Sub-question 3: What is the id of GNMT?\n'
		prompt += f'[{url_10}]->[{response10}]\n'
		prompt += f'Task 3: Extract chromosome location of GNMT. Sub-question 4: What is the chromosome location of GNMT?\n'
		prompt += f'[{url_11}]->[{response11}]\n'
		prompt += f'Answer: 6p21.1\n\n'

		# too long 
		# prompt += f'Question:List chromosome locations of the genes related to Hemolytic anemia due to phosphofructokinase deficiency. Let us decompose the question to sub-questions and solve them step by step:\n'
		# prompt += f'Sub-question 1: What is the OMIM id of Glycine N-methyltransferase deficiency?\n'
		# prompt += f'[{url_8}]->[{call_8}]\n'
		# prompt += f'Task 1: Extract the OMIM id in the list:[606664,606628,601240,160993]. Sub-question 2: What are genes related to OMIM id 606664,606628,601240,160993?\n'
		# prompt += f'[{url_9}]->[{call_9}]\n'
		# prompt += f'Task 2: Extract Gene symbol in the title: GNMT. Sub-question 3: What is the chromosome location of GNMT?\n'
		# prompt += f'[{url_10}]->[{call_10}]\n'
		# prompt += f'[{url_11}]->[{call_11}]\n'
		# prompt += f'Answer: 6p21.1\n\n'

	return prompt

def main():
	logger.info("Starting the GeneGPT execution process")
	cut_length = 36000
	mask = [bool(int(x)) for x in str_mask] 
	prompt = get_prompt_header(mask) 

	if not os.path.isdir(results_dir):
		os.mkdir(results_dir)

	output_dir = os.path.join(results_dir, str_mask)
	if not os.path.isdir(output_dir):
		os.mkdir(output_dir)

	#Read the question and standard answer qas
	qas = json.load(open(input_file)) 

	for task, info in qas.items():
		if os.path.exists(os.path.join(output_dir, f'{task}.json')): 
			preds = json.load(open(os.path.join(output_dir, f'{task}.json'))) 
			if len(preds) == 50: continue 
			output = preds 
		else:
			output = []

		# Extract the completed set of questions to avoid duplicate processing
		done_questions = set([entry[0] for entry in output])

		logger.info(f'Doing task {task}')
		for question, answer in info.items(): 
			if question in done_questions:
				continue
			print('---------------------------------New Instance---------------------------------')
			logger.info('---------------------------------New Instance---------------------------------')
			print(question)
			q_prompt = prompt + f'Question: {question}\n'
			prompts = [] 
			num_calls = 0

			while True:
				if len(q_prompt) > cut_length:
					q_prompt = q_prompt[len(q_prompt) - cut_length:]

				try:
					time.sleep(10)
					text = call_ollama(q_prompt,num_calls)
				except Exception as e:
					output.append([question, answer, 'Error', prompts])
					break

				num_calls += 1
				prompts.append([q_prompt, text]) 

				url_regex = r'\[(https?://[^\[\]]+)\]' 
				matches = re.findall(url_regex, text)

				if matches:
					call_responses = []  
					for url in matches:  
						if 'blast' in url and 'Get' in url: time.sleep(30) 
						call = call_api(url) 

						if call is None:
							logger.error(f"API call failed for URL: {url}. Skipping to the next iteration.")
							call_responses.append("[Error: API call failed]") 
							break

						if 'blast' in url and 'Put' in url:
							rid = re.search('RID = (.*)\n', call.decode('utf-8')).group(1) 
							call = rid

						if len(call) > 20000:
							call = call[:20000]

						if isinstance(call, bytes):
							call = call.decode('utf-8') 

						call_responses.append(call)
					q_prompt = f"{q_prompt}{text}->[{'; '.join(call_responses)}]\n"

				else:
					output.append([question, answer, text, prompts])
					break

				if num_calls >= 10: 
					logger.error("Reached maximum API calls limit (10), exiting loop.")
					output.append([question, answer, 'numError', prompts])
					break

			with open(os.path.join(output_dir, f'{task}.json'), 'w') as f:
				json.dump(output, f, ensure_ascii=False, indent=4)

	logger.info("GeneGPT execution process completed")

if __name__ == '__main__':
	main()