from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage,HumanMessage, AIMessage, ToolMessage
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

class Generator:
    def __init__(self):
        self.llm = ChatOllama(
            model="qwen2.5:14b",
            base_url="xxxxxxxxxxxxxx",
            api_key="ollama",
            num_ctx=16000,
            temperature=0
        )
    
    def generate(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Keep metadata
        metadata = state.get("metadata", {})
        messages = state["messages"]
        
        # Check if the request is not related to bioinformatics
        if metadata.get("routing_reason") == "IRRELEVANT REQUEST.":
            irrelevant_prompt = """
You are a strict bio-information assistant. The user has asked a question that is not related to bioinformatics.
Please generate a polite response that:
1. Explains you are a bio-information assistant
2. Clarifies the types of questions you can answer (genes, proteins, diseases, sequences, etc.)
3. Politely declines to answer the current question
4. Keep the response concise and professional
"""
            response = self.llm.invoke([SystemMessage(content=irrelevant_prompt)])
            
            return {
                "messages": messages + [
                    AIMessage(
                        content=response.content,
                        additional_kwargs={"type": "final_answer"}
                    )
                ],
                "next": "END",
                "metadata": metadata,
                "thinking_content": "User question is not related to bioinformatics, generate a polite response to decline."
            }

        # Get all user messages
        user_messages = [msg for msg in messages if isinstance(msg, HumanMessage)]

        agent_messages = [
            msg for msg in messages
            if isinstance(msg, (AIMessage, ToolMessage))
        ]
        
        if not user_messages:
            return {
                "status": "error",
                "error": "No user question found",
                "metadata": metadata,
                "thinking_content": "No user question found"
            }
        
        # Get first user question
        original_question = user_messages[0].content

        # If eval_count, record log
        if metadata.get("eval_count"):
            logger.info(f"Generate final answer (after {metadata['eval_count']} evaluations)")
        else:
            logger.info("Generate final answer...")

        # Build history text
        history_text = ""
        for msg in agent_messages:
            msg_type = msg.additional_kwargs.get("type", "unknown")
            history_text += f"\n--- {msg_type} ---\n{msg.content}\n"
        
        combined_prompt = f"""
USER QUESTION:
{original_question}
--------------------------------
PREVIOUS RESULTS AND ANALYSIS:
{history_text if history_text else "No previous analysis available."}
--------------------------------
You are a bioinformatician. Based on the above conversation history and research results, answer the user's question.
Please adhere to the following requirements:
1. The answer should be direct and clear
2. Don't add unnecessary foreshadowing
3. Use the information gathered from the tools (E-utils, BLAST, Web search etc.) to provide an accurate response
4. If the information is insufficient, acknowledge the limitations

Please generate your final answer now.
"""
        
        response = self.llm.invoke([SystemMessage(content=combined_prompt)])
        
        logger.info("Answer generated")
        
        # Return generated answer
        return {
            "messages": messages + [
                AIMessage(
                    content=response.content,
                    additional_kwargs={"type": "final_answer"}
                )
            ],
            "metadata": {
                **metadata,
                "thinking_content": f"Generate final answer."
            }
        }
