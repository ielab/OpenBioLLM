from .call_api import call_api
import re
import time
from typing import Dict, List, Tuple

class ExampleManager:
	def __init__(self):
		self.examples = {
			2: {  # Example 1: gene alias task
				'urls': [
					('esearch', 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gene&retmax=5&retmode=json&sort=relevance&term=LMP10'),
					('efetch', 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=gene&retmax=5&retmode=json&sort=relevance&id=19171,5699,8138')
				],
				'question': 'What is the official gene symbol of LMP10?',
				'answer': 'PSMB10'
			},
			3: {  # Example 2: SNP gene task
				'urls': [
					('esummary', 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=snp&retmax=10&retmode=json&sort=relevance&id=1217074595')
				],
				'question': 'Which gene is SNP rs1217074595 associated with?',
				'answer': 'LINC01270'
			},
			4: {  # Example 3: gene disease association
				'urls': [
					('esearch', 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=omim&retmax=20&retmode=json&sort=relevance&term=Meesmann+corneal+dystrophy'),
					('esummary', 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=omim&retmax=20&retmode=json&sort=relevance&id=618767,601687,300778,148043,122100')
				],
				'question': 'What are genes related to Meesmann corneal dystrophy?',
				'answer': 'KRT12, KRT3'
			},
			5: {  # Example 4: BLAST
				'urls': [
					('blast_put', 'https://blast.ncbi.nlm.nih.gov/blast/Blast.cgi?CMD=Put&PROGRAM=blastn&MEGABLAST=on&DATABASE=nt&FORMAT_TYPE=XML&QUERY=ATTCTGCCTTTAGTAATTTGATGACAGAGACTTCTTGGGAACCACAGCCAGGGAGCCACCCTTTACTCCACCAACAGGTGGCTTATATCCAATCTGAGAAAGAAAGAAAAAAAAAAAAGTATTTCTCT&HITLIST_SIZE=5')
				],
				'question': 'Align the DNA sequence to the human genome:ATTCTGCCTTTAGTAATTTGATGACAGAGACTTCTTGGGAACCACAGCCAGGGAGCCACCCTTTACTCCACCAACAGGTGGCTTATATCCAATCTGAGAAAGAAAGAAAAAAAAAAAAGTATTTCTCT',
				'answer': 'chr15:91950805-91950932'
			}
		}

	def get_example_content(self, example_id: int) -> Tuple[str, List[str], str]:
		"""Get example content and perform necessary API calls"""
		example = self.examples.get(example_id)
		if not example:
			return "", [], ""
		
		api_results = []
		for api_type, url in example['urls']:
			result = call_api(url)
			
			# Special handling for BLAST
			if api_type == 'blast_put':
				rid = re.search('RID = (.*)\n', result.decode('utf-8')).group(1)
				time.sleep(30)  # Wait for BLAST results
				get_url = f'https://blast.ncbi.nlm.nih.gov/blast/Blast.cgi?CMD=Get&FORMAT_TYPE=Text&RID={rid}'
				result = call_api(get_url)
				api_results.extend([f'[{url}]->\n[{rid}]', f'[{get_url}]->\n[{result}]'])
			else:
				api_results.append(f'[{url}]->\n[{result}]')
		
		return example['question'], api_results, example['answer']

def get_prompt_header(mask: List[int]) -> str:
	'''
    mask: [1/0 x 6], denotes whether each prompt component is used
    output: prompt
    '''
	prompt = 'Hello. Your task is to use NCBI Web APIs to answer genomic questions.\n'
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
		
		# Initialize example manager
		example_manager = ExampleManager()
		
		# Add enabled examples
		for i in range(2, len(mask)):
			if mask[i]:
				question, api_results, answer = example_manager.get_example_content(i)
				if question:
					prompt += f'Question: {question}\n'
					prompt += '\n'.join(api_results) + '\n'
					prompt += f'Answer: {answer}\n\n'

	return prompt