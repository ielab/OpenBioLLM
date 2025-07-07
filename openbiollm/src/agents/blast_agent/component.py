import re
import logging
import time
import json
from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from langchain_ollama import ChatOllama
from ...tools.call_api import call_api
# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

class BlastComponent:
    def __init__(self):
        self.llm = ChatOllama(
            model="qwen2.5:14b",
            base_url="xxxxxxxxxxxxxx",
            api_key="ollama",
            num_ctx=16000,
            temperature=0
        )
    
    def is_duplicate_params(self, new_params: Dict[str, Any], used_params: List[Dict[str, Any]]) -> bool:
        """
        Check if BLAST parameters are duplicate
        Only check sequence, hitlist_size can be different
        """
        for old_params in used_params:
            # Only check if sequence is the same
            if new_params.get('sequence') == old_params.get('sequence'):
                return True
        return False

    def init_blast_query(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Step 1: Initialize BLAST query, generate PUT request"""
        # Ensure metadata is preserved
        metadata = state.get("metadata", {})
        messages = state["messages"]
        
        # Get history parameter records
        used_params = metadata.get("used_blast_params", [])
        
        # Get all user messages
        user_question = [msg for msg in messages if isinstance(msg, HumanMessage) and msg.additional_kwargs.get("type") == "user_question"]
        
        # Get previous BLAST operation history
        agent_history = [
            msg for msg in messages 
            if isinstance(msg, AIMessage) and 
            msg.additional_kwargs.get("type") in ["blast_progress", "blast_response", "eutils_progress", "eutils_response"]
        ]
        
        if not user_question:
            return {
                "status": "error",
                "error": "No user question found",
                "metadata": metadata,
                "thinking_content": "没有找到用户问题"
            }
        
        # Get the first user question
        original_question = user_question[0].content
        logger.info(f"Initialize BLAST query: {original_question}")
        
        # Format history as text
        history_text = ""
        for msg in agent_history:
            msg_type = msg.additional_kwargs.get("type", "unknown")
            history_text += f"\n--- {msg_type} ---\n{msg.content}\n"
        
        # Format used parameters
        used_params_text = ""
        if used_params:
            used_params_text = "\nPreviously used sequences(for reference):\n"
            for i, params in enumerate(used_params, 1):
                used_params_text += f"{i}. {params['sequence'][:50]}...\n"
        
        combined_prompt = f"""

You are a parameter extractor for NCBI BLAST API. You need to extract the DNA sequence from the user's question.
If there were previous BLAST operations, review them to understand if a new query is needed or if we should work with existing results.

Here is an example:
Question: Align the DNA sequence to the human genome: ATTCTGCCTTTAGTAATTTGATGACAGAGACTTCTTGGGAACCACAGCCAGGGAGCCACCCTTTACTCCACCAACAGGTGGCTTATATCCAATCTGAGAAAGAAAGAAAAAAAAAAAAGTATTTCTCT?
Output: {{"sequence": "ATTCTGCCTTTAGTAATTTGATGACAGAGACTTCTTGGGAACCACAGCCAGGGAGCCACCCTTTACTCCACCAACAGGTGGCTTATATCCAATCTGAGAAAGAAAGAAAAAAAAAAAAGTATTTCTCT","hitlist_size": 10}}

--------------------------------
USER QUESTION:
{original_question}
--------------------------------
PREVIOUS HISTORY:
{history_text if history_text else "No previous interaction history."}
--------------------------------
PREVIOUS USED SEQUENCES (for reference):
{used_params_text if used_params_text else "No previous used sequences."}
--------------------------------

Extract relevant search terms from the user's question and the previous history.
IMPORTANT: 
1. Only return a JSON object with these keys DIRECTLY, do NOT include any other text or comments.
2. Try to use a different sequence if the desired sequence has already been used, but accuracy is more important than uniqueness.
"""
        
        blast_prompt = [SystemMessage(content=combined_prompt)]
        
        try:
            response = self.llm.invoke(blast_prompt)
            
            # Parse JSON response
            try:
                params = json.loads(response.content)
            except json.JSONDecodeError:
                json_match = re.search(r'({.*?})', response.content.replace('\n', ''))
                if not json_match:
                    logger.error(f"Cannot extract valid JSON from LLM response: {response}")
                    return {
                        "messages": messages + [
                            AIMessage(content="Cannot extract valid JSON from LLM response",
                                    additional_kwargs={"type": "blast_error"})
                        ],
                        "status": "error",
                        "metadata": {
                            **metadata,
                            "thinking_content": "Cannot extract valid JSON from LLM response"
                        }
                    }
                params = json.loads(json_match.group(1))

            # Use duplicate check method
            if self.is_duplicate_params(params, used_params):
                logger.warning(f"Duplicate sequence detected: {params['sequence'][:50]}...")
                return {
                    "messages": messages + [
                        AIMessage(content="This sequence has been used before. Please try with a different sequence or rephrase your question to use a new sequence.",
                                additional_kwargs={"type": "blast_error"})
                    ],
                    "status": "error",
                    "metadata": {
                        **metadata,
                        "thinking_content": "Duplicate sequence detected"
                    }
                }

            # Verify if necessary parameters exist
            if "sequence" not in params:
                logger.error(f"Missing required sequence parameter: {params}")
                return {
                    "messages": messages + [
                        AIMessage(content="Missing required sequence parameter",
                                additional_kwargs={"type": "blast_error"})
                    ],
                    "status": "error",
                    "metadata": {
                        **metadata,
                        "thinking_content": "Missing required sequence parameter"
                    }
                }

            # Build BLAST URL
            url = "https://blast.ncbi.nlm.nih.gov/blast/Blast.cgi?CMD=Put&PROGRAM=blastn&MEGABLAST=on&DATABASE=nt&FORMAT_TYPE=XML"
            url += f"&QUERY={params['sequence']}"
            if "hitlist_size" in params:
                url += f"&HITLIST_SIZE={params['hitlist_size']}"
            else:
                url += "&HITLIST_SIZE=10"  # Default value

            logger.info(f"Generated BLAST URL: {url}")
            
            # Send PUT request
            api_response = call_api(url)
            if api_response is None:
                return {
                    "messages": messages + [
                        AIMessage(content="BLAST Put request failed",
                                additional_kwargs={"type": "blast_error"})
                    ],
                    "status": "error",
                    "metadata": {
                        **metadata,
                        "thinking_content": "BLAST Put request failed"
                    }
                }
            
            # Extract RID
            rid_match = re.search('RID = (.*)\n', api_response.decode('utf-8'))
            if not rid_match:
                logger.error("Cannot extract RID from BLAST response")
                return {
                    "messages": messages + [
                        AIMessage(content="Could not extract RID from BLAST response",
                                additional_kwargs={"type": "blast_error"})
                    ],
                    "status": "error",
                    "metadata": {
                        **metadata,
                        "thinking_content": "Could not extract RID from BLAST response"
                    }
                }
                
            rid = rid_match.group(1)
            
            # Record used parameters
            used_params.append(params)
            
            # Return result, update metadata
            return {
                "messages": messages + [
                    AIMessage(
                        content=f"Initiated BLAST query with: [{url}]\nReceived RID: {rid}",
                        additional_kwargs={
                            "type": "blast_progress",
                            "parameters": params  # Save parameters in message for easy viewing
                        }
                    )
                ],
                "next": "fetch_results",
                "metadata": {
                    **metadata,
                    "blast_rid": rid,
                    "attempt": 0,
                    "used_blast_params": used_params,  # Update used parameters list
                    "thinking_content": f"Initialize BLAST query: {url}, RID: {rid}"
                }
            }
            
        except Exception as e:
            logger.error(f"Error initializing BLAST query: {str(e)}")
            return {
                "messages": messages + [
                    AIMessage(content=f"Error initializing BLAST query: {str(e)}",
                            additional_kwargs={"type": "blast_error"})
                ],
                "status": "error",
                "metadata": {
                    **metadata,
                    "thinking_content": f"Error initializing BLAST query: {str(e)}"
                }
            }
    
    def fetch_blast_results(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Step 2: Fetch BLAST query results"""
        metadata = state.get("metadata", {})
        messages = state["messages"]
        
        # Get saved RID
        rid = metadata.get("blast_rid")
        if not rid:
            logger.error("No RID found for BLAST query")
            return {
                "messages": messages + [
                    AIMessage(content="No RID found for BLAST query",
                            additional_kwargs={"type": "blast_error"})
                ],
                "status": "error",
                "metadata": {
                    **metadata,
                    "thinking_content": "No RID found for BLAST query"
                }
            }
        
        # Get current attempt count
        attempt = metadata.get("attempt", 0)
        metadata["attempt"] = attempt + 1
        
        logger.info(f"Attempting to fetch BLAST results, RID: {rid}, attempt: {attempt+1}")
        
        # Build GET request URL
        get_url = f"https://blast.ncbi.nlm.nih.gov/blast/Blast.cgi?CMD=Get&FORMAT_TYPE=Text&RID={rid}"
        
        # Wait for a while before fetching results
        waiting_time = min(15 * (attempt + 1), 60)  # Wait time increases with attempt count, max 60 seconds
        logger.info(f"Waiting {waiting_time} seconds before fetching results...")
        time.sleep(waiting_time)
        
        # Send GET request
        api_response = call_api(get_url)
        
        if api_response is None:
            if attempt < 3:  # Max 3 attempts
                return {
                    "messages": messages + [
                        AIMessage(content=f"Waiting for BLAST results (attempt {attempt+1}/3)...",
                                additional_kwargs={"type": "blast_progress"})
                    ],
                    "next": "fetch_results",  # Try again
                    "metadata": {
                        **metadata,
                        "thinking_content": f"Waiting for BLAST results (attempt {attempt+1}/3)..."
                    }
                }
            else:
                return {
                    "messages": messages + [
                        AIMessage(content="Failed to retrieve BLAST results after multiple attempts",
                                additional_kwargs={"type": "blast_error"})
                    ],
                    "status": "error",
                    "metadata": {
                        **metadata,
                        "thinking_content": "Failed to retrieve BLAST results after multiple attempts"
                    }
                }
        
        # Check if still running
        response_text = api_response.decode('utf-8')
        if "Status=WAITING" in response_text or "is still running" in response_text:
            if attempt < 3:  # Max 3 attempts
                return {
                    "messages": messages + [
                        AIMessage(content=f"BLAST analysis still running (attempt {attempt+1}/3)...",
                                additional_kwargs={"type": "blast_progress"})
                    ],
                    "next": "fetch_results",  # Try again
                    "metadata": {
                        **metadata,
                        "thinking_content": f"BLAST analysis still running (attempt {attempt+1}/3)..."
                    }
                }
            else:
                return {
                    "messages": messages + [
                        AIMessage(content="BLAST analysis is taking too long, please try again later",
                                additional_kwargs={"type": "blast_error"})
                    ],
                    "status": "error",
                    "metadata": {
                        **metadata,
                        "thinking_content": "BLAST analysis is taking too long, please try again later"
                    }
                }
        
        # Crop long results
        if len(response_text) > 10000:
            response_text = response_text[:10000] + "... [result is truncated]"
        
        return {
            "messages": messages + [
                AIMessage(
                    content=f"BLAST Results:\n\n{response_text}",
                    additional_kwargs={
                        "type": "blast_response",
                        "url": get_url,
                        "rid": rid
                    }
                )
            ],
            "metadata": {
                **metadata,
                "thinking_content": f"BLAST results fetched"
            }
        }