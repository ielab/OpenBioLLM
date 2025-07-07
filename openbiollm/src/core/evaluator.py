from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, AIMessage,HumanMessage, ToolMessage
import logging
from typing import Dict, Any
from textwrap import dedent
import json
import re

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

class Evaluator:
    def __init__(self):
        self.llm = ChatOllama(
            model="qwen2.5:14b",
            base_url="http://34.142.153.30:11434",
            api_key="ollama",
            num_ctx=16000,
            temperature=0
        )

    
    def evaluate(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Get or initialize evaluator counter
        if "metadata" not in state:
            state["metadata"] = {}
        
        if "eval_count" not in state["metadata"]:
            state["metadata"]["eval_count"] = 0
        
        # Increment evaluator counter
        state["metadata"]["eval_count"] += 1
        eval_count = state["metadata"]["eval_count"]
        
        # Check if evaluation limit is reached
        if eval_count >= 5:
            logger.info(f"Evaluation limit reached ({eval_count}/5), force to generate")
            return {
                "next": "generate",
                "metadata": {
                    **state["metadata"],
                    "thinking_content": "Evaluation count limit reached, force to generate"
                }
            }

        messages = state["messages"]
        # Get all user messages
        user_question = [msg for msg in messages if isinstance(msg, HumanMessage) and msg.additional_kwargs.get("type") == "user_question"]

        if not user_question:
            return {
                "status": "error",
                "error": "No user question found",
                "metadata": {
                    **state["metadata"],
                    "thinking_content": "No user question found"
                }
            }
        
        # Get first user question
        original_question = user_question[0].content

        # Get system message
        system_message = [msg for msg in messages if isinstance(msg, SystemMessage) and msg.additional_kwargs.get("type") == "system_prompt"]

        # Get related history messages
        agent_history = [
            msg for msg in messages
            if (
                (isinstance(msg, AIMessage) and msg.additional_kwargs.get("type") in [
                    "blast_progress", "blast_response",
                    "eutils_progress", "eutils_response",
                    "search_response"
                ])
                or isinstance(msg, ToolMessage)
            )
        ]

        # Format history as text
        history_text = ""
        for msg in agent_history:
            msg_type = msg.additional_kwargs.get("type", "unknown")
            history_text += f"\n--- {msg_type} ---\n{msg.content}\n"

        
        # Use LLM to evaluate if information is sufficient

        eval_prompt = [
        SystemMessage(content=f"""\
You are a strict answer evaluator.
You should make a decision about whether the conversation history can answer the question.
You need to return a JSON object with the following structure:
{{
    "next_step": "GENERATE" or "CONTINUE",
    "reason": "Brief explanation of your decision"
}}

Examples:
1. When information is sufficient:
{{
    "next_step": "GENERATE",
    "reason": "Found the official gene symbol Psmb10 in the results"
}}

2. When information is insufficient:
{{
    "next_step": "CONTINUE",
    "reason": "Only have gene IDs, need detailed gene information"
}}

--------------------------------
USER QUESTION: {original_question}
--------------------------------
CONVERSATION HISTORY:
{history_text if history_text else "No previous conversation history."}
--------------------------------
Please return your decision as a JSON object.
""")
        ]
        
        try:
            response = self.llm.invoke(eval_prompt)
            
            # Parse JSON response
            try:
                eval_result = json.loads(response.content)
            except json.JSONDecodeError:
                json_match = re.search(r'({.*?})', response.content.replace('\n', ''))
                if not json_match:
                    logger.error(f"Cannot extract valid JSON from evaluator response: {response.content}")
                    return {
                        "next": "router",
                        "metadata": {
                            **state["metadata"],
                            "eval_error": "Invalid JSON response from evaluator",
                            "thinking_content": "Invalid JSON response from evaluator"
                        }
                    }
                eval_result = json.loads(json_match.group(1))
            
            logger.info(f"Evaluator decision: {eval_result} (evaluation count: {eval_count}/5)")
            
            if eval_result["next_step"] == "CONTINUE":
                logger.info(f"Information insufficient, return router to continue querying. Reason: {eval_result['reason']}")
                return {
                    "next": "router",
                    "metadata": {
                        **state["metadata"],
                        "eval_result": eval_result,
                        "thinking_content": f"Information is insufficient, return router to continue querying.{eval_result['reason']}"
                    }
                }
            elif eval_result["next_step"] == "GENERATE":
                logger.info(f"Information sufficient, enter generate stage. Reason: {eval_result['reason']}")
                return {
                    "next": "generate",
                    "metadata": {
                        **state["metadata"],
                        "eval_result": eval_result,
                        "thinking_content": f"Information is sufficient, enter generate stage.{eval_result['reason']}"
                    }
                }
            else:
                logger.info("Invalid decision, return router to continue querying")
                return {
                    "next": "router",
                    "metadata": {
                        **state["metadata"],
                        "eval_error": "Invalid decision from evaluator",
                        "thinking_content": "Invalid decision from evaluator, return router to continue querying"
                    }
                }
            
        except Exception as e:
            logger.error(f"Evaluation error: {str(e)}")
            return {
                "next": "router",
                "metadata": {
                    **state["metadata"],
                    "eval_error": f"Evaluation error: {str(e)}",
                    "thinking_content": f"Evaluation error: {str(e)}"
                }
            }
