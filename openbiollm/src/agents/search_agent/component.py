from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, ToolMessage
import requests
import uuid

class SearchComponent:
    def __init__(self):
        self.api_key = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'  # Replace with your actual API key
        self.cse_id = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'  # Replace with your actual Custom Search Engine ID

    def _safe_get_metatag(self, metatags: List[dict], key: str) -> str:
        try:
            return metatags[0].get(key, '') if metatags else ''
        except (IndexError, AttributeError):
            return ''

    def _safe_get_first_item(self, items: List[dict], key: str) -> str:
        try:
            return items[0].get(key, '') if items else ''
        except (IndexError, AttributeError):
            return ''

    def google_search(self, query, num=5):
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "q": query,
            "key": self.api_key,
            "cx": self.cse_id,
            "num": num
        }
        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status() 
            data = resp.json()
            results = []
            
            for item in data.get("items", []):
                pagemap = item.get('pagemap', {})
                metatags = pagemap.get('metatags', [])
                article = pagemap.get('article', [])
                person = pagemap.get('person', [])
                
                result = {
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                    "domain": item.get("displayLink", ""),
                    "keywords": self._safe_get_first_item(article, "keywords"),
                    "publish_date": self._safe_get_first_item(article, "datepublished"),
                    "author": next((p.get("name") for p in person if p.get("name")), ""),
                    "full_description": self._safe_get_metatag(metatags, "og:description") or item.get("snippet", "")
                }
                
                result = {k: v if v is not None else "" for k, v in result.items()}
                results.append(result)
                
            return results
            
        except requests.exceptions.RequestException as e:
            print(f"Search request error: {str(e)}")
            return []
        except ValueError as e:
            print(f"JSON parsing error: {str(e)}")
            return []
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return []

    def extract_related_text(self, related):
        texts = []
        for item in related:
            if "Text" in item:
                texts.append(item["Text"])
            elif "Topics" in item:
                texts.extend(self.extract_related_text(item["Topics"]))
        return texts

    def init_search(self, state: Dict[str, Any]) -> Dict[str, Any]:
        messages = state["messages"]
        user_question = [msg for msg in messages if isinstance(msg, HumanMessage)]
        
        if not user_question:
            return {
                "status": "error",
                "error": "No user question found",
                "metadata": state.get("metadata", {})
            }
        question = user_question[0].content

        try:
            results = self.google_search(question)
            if not results:
                context = "No relevant information found from Google Search."
            else:
                context_parts = []
                for item in results:
                    context_part = []
                    if item['title']:
                        context_part.append(f"Title: {item['title']}")
                    if item['domain']:
                        context_part.append(f"Source: {item['domain']}")
                    if item['publish_date']:
                        context_part.append(f"Date: {item['publish_date']}")
                    if item['author']:
                        context_part.append(f"Author: {item['author']}")
                    if item['full_description'] or item['snippet']:
                        context_part.append(f"Summary: {item['full_description'] or item['snippet']}")
                    if item['keywords']:
                        context_part.append(f"Keywords: {item['keywords']}")
                    if item['link']:
                        context_part.append(f"URL: {item['link']}")
                    
                    context_parts.append("\n".join(context_part))
                
                context = "\n\n".join(context_parts)
                
        except Exception as e:
            context = f"Error fetching Google Search results: {str(e)}"

        tool_msg = ToolMessage(
            content=f"[google_search: \"{question}\"]->[{context}]",
            name="google_search",
            tool_call_id=str(uuid.uuid4()),
            additional_kwargs={
                "type": "search_response",
                "results": results if results else []
            }
        )

        return {
            "messages": messages + [tool_msg],
            "next": "evaluator",
            "metadata": {
                **state.get("metadata", {}),
                "search_results": results if results else []
            }
        }