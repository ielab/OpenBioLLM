from langchain_ollama import ChatOllama
import logging
import json
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

class Router:
    def __init__(self):
        self.llm = ChatOllama(
            model="qwen2.5:14b",
            base_url="xxxxxxxxxxxxxx",
            api_key="ollama",
            num_ctx=16000,
            temperature=0
        )
    
    def route(self, state):
        # Keep metadata
        metadata = state.get("metadata", {})
        messages = state["messages"]
        
        # Get user question
        user_question = [msg for msg in messages if isinstance(msg, HumanMessage)]
        
        # Get history
        agent_history = [
            msg for msg in messages
            if isinstance(msg, AIMessage) and
            (msg.additional_kwargs.get("type") in ["eutils_response", "eutils_progress", "blast_response", "blast_progress", "search_response"])
        ]
        
        if not user_question:
            return {
                "status": "error",
                "error": "No user question found",
                "metadata": {
                    **metadata,
                    "thinking_content": "No user question found"
                }
            }
        
        # Extract user question text
        original_question = user_question[0].content
        
        # Format history text
        history_text = ""
        for msg in agent_history:
            msg_type = msg.additional_kwargs.get("type", "unknown")
            history_text += f"\n--- {msg_type} ---\n{msg.content}\n"
        
        # Get evaluator's opinion
        eval_result = metadata.get("eval_result", {})
        eval_reason = eval_result.get("reason", "No evaluation reason provided")
        
        combined_prompt = f"""
You are a strict router that uses JSON to make routing decisions. You should analyze the conversation history above to make an informed decision about which agent to use.
router options:
   - eutils_agent: query the database to get the detail information about gene, protein, disease.
   - blast_agent: check the DNA sequence alignment and comparison.
   - search_agent: search the web when you find there are a lot of eutils or blast call in conversation history but still cannot answer the question.
   - irrelevant_questions: the question is not related to bioinformatics.

                                     
You should consider the following:
   - What is the question?
   - What information we have gathered so far?
   - Which tool would be most appropriate for the next step?
   - The evaluator's opinion.

--------------------------------
USER QUESTION: 
{original_question}
--------------------------------
CONVERSATION HISTORY:
{history_text if history_text else "No previous interaction history."}
--------------------------------
PREVIOUS EVALUATOR'S OPINION:
{eval_reason}
--------------------------------

You MUST output your decision in the following JSON format:
{{
    "agent": "eutils_agent" or "blast_agent" or "search_agent" or "irrelevant_questions",
    "reason": "Brief explanation of why this agent was chosen for the next step"
}}
                                     
Do not include any other text or formatting. ONLY return the JSON object.
"""
        
        router_prompt = [SystemMessage(content=combined_prompt)]
        
        # Add retry mechanism
        max_retries = 3
        for attempt in range(max_retries):
            response = self.llm.invoke(router_prompt)
            
            try:
                # Try to parse JSON response
                response_json = json.loads(response.content)
                
                # Verify JSON format
                if "agent" in response_json and "reason" in response_json:
                    agent = response_json["agent"]
                    reason = response_json["reason"]
                    
                    if agent in ["eutils_agent", "blast_agent", "search_agent","irrelevant_questions"]:
                        # Record routing decision and reason
                        logger.info(f"Routing decision: {agent}, reason: {reason}")
                        return {
                            "next": agent,
                            "metadata": {
                                **metadata,
                                "routing_reason": "IRRELEVANT REQUEST." if agent == "irrelevant_questions" else reason,
                                "thinking_content": f"{agent} was chosen for the next step. Reason: {reason}"
                            }
                        }
                    else:
                        logger.warning(f"Unknown agent: {agent}")
                else:
                    logger.warning(f"JSON response format is incorrect: {response_json}")
            except json.JSONDecodeError:
                logger.warning(f"Try {attempt + 1}/{max_retries}: cannot parse JSON: {response.content}")
            
            logger.warning(f"Try {attempt + 1}/{max_retries}: {response.content}")
        
        # Default to eutils
        logger.warning("Multiple attempts failed, default to eutils")
        return {
            "next": "eutils_agent",
            "metadata": {
                **metadata,
                "thinking_content": "Failed to route, default to eutils"
            }
        }
        
    