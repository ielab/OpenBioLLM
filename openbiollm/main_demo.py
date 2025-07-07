from src.core.settings import configure_settings
from src.core.rag import initialize_rag_system
from langchain_core.messages import HumanMessage, SystemMessage
from src.tools.get_prompt_header import get_prompt_header

def main():
    configure_settings()
    workflow = initialize_rag_system()

    # Prepare question list
    questions = [
        # GeneTuring examples
        # "What is the official gene symbol of SNAT6?"  #SLC38A6
        # "What are genes related to Distal renal tubular acidosis?"  #SLC4A1, ATP6V0A4
        # "Which chromosome is TTTY7 gene located on human genome?"  #chrY
        # "Align the DNA sequence to the human genome:GGACAGCTGAGATCACATCAAGGATTCCAGAAAGAATTGGCACAGGATCATTCAAGATGCATCTCTCCGTTGCCCCTGTTCCTGGCTTTCCTTCAACTTCCTCAAAGGGGACATCATTTCGGAGTTTGGCTTCCA"  #chr8:7081648-7081782
        # "Which organism does the DNA sequence come from:CGTACACCATTGGTGCCAGTGACTGTGGTCAATTCGGTAGAAGTAGAGGTAAAAGTGCTGTTCCATGGCTCAGTTGTAGTTATGATGGTGCTAGCAGTTGTTGGAGTTCTGATGACAATGACGGTTTCGTCAGTTG"  #yeast
        # "Convert ENSG00000205403 to official gene/ symbol."  #CFI
        # "Is LOC124907753 a protein-coding gene?"  #N/A
        # "Which gene is SNP rs1241371358 associated with?"  #LRRC23
        # "Which chromosome does SNP rs545148486 locate on human genome?"  #chr16

        # GeneHop examples
        # "What is the function of the gene associated with SNP rs1241371358? Let's decompose the question to sub-questions and solve them step by step."  # Predicted to be active in cytosol.
        # "List chromosome locations of the genes related to Hemolytic anemia due to phosphofructokinase deficiency. Let's decompose the question to sub-questions and solve them step by step."  #"21q22.3"
        # "What are the aliases of the gene that contains this sequnece:ATTGTGAGAGTAACCAACGTGGGGTTACGGGGGAGAATCTGGAGAGAAGAGAAGAGGTTAACAACCCTCCCACTTCCTGGCCACCCCCCTCCACCTTTTCTGGTAAGGAGCCC. Let's decompose the question to sub-questions and solve them step by step."
       
        # "NBA playoff schedule" # example to show irrelevant questions
        # "Which signaling pathways is TP53 involved in?" # example to show search agent
        "What are the potential side effects of CRISPR gene editing in clinical trials?"

    ]

    # Process each question
    for question in questions:
        print("\n" + "="*50)
        print(f"Question: {question}")
        
        # Create input - add system prompt as the first message
        inputs = {
            "messages": [
                HumanMessage(content=question, additional_kwargs={"type": "user_question"})
            ]
        }
        
        # Execute workflow and get output
        for output in workflow.stream(inputs):
            node_name = list(output.keys())[0]
            node_output = output[node_name]
            
            print("\n" + "="*50)
            print(f"Node: {node_name}")
            
            # If it's a message list, only take the last message content
            if isinstance(node_output, dict) and "messages" in node_output:
                latest_message = node_output["messages"][-1].content
                print(f"Output: {latest_message}")
            else:
                print(f"Output: {node_output}")
            print("="*50)

if __name__ == "__main__":
    main()