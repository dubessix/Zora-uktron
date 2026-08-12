"""
Ultron Real Deep Research Tool
Asynchronously connects to the Tavily Search API using the configured TAVILY_API_KEY to retrieve
multi-source web summaries, URLs, and research data.
"""

import os
import httpx
from typing import Dict, Any
from pydantic import BaseModel, Field
from backend.app.tools.tool_base import BaseTool

class ResearchArgs(BaseModel):
    query: str = Field(..., description="Target search query topic for deep multi-source research.")

class TavilyResearchTool(BaseTool):
    def __init__(self) -> None:
        super().__init__(
            tool_id="tavily_research",
            name="Deep AI Research",
            description="Executes semantic web searches across multi-source registries and returns structured summaries.",
            category="research",
            tags=["research", "search", "web", "tavily", "google", "summary"],
            permission_level=0, # Level 0: Read-Only (no confirmation)
            args_model=ResearchArgs,
            usage_examples=["tavily_research(query='latest AI agents frameworks')"]
        )

    async def execute(self, **kwargs) -> Dict[str, Any]:
        query_str = kwargs.get("query", "")
        api_key = os.getenv("TAVILY_API_KEY")
        
        # If no key is set or is placeholder, use real (free, keyless) web results
        # instead of a fake summary, and open the top answer page in the browser.
        if not api_key or "your_tavily_api_key" in api_key:
            try:
                import webbrowser
                from backend.app.tools._realsearch import real_web_search
                results = await real_web_search(query_str, limit=3)
                if results:
                    # Open the most relevant answer page in the browser (not a search URL).
                    top_url = results[0]["url"]
                    try:
                        webbrowser.open(top_url)
                    except Exception:
                        pass
                    sources = [
                        {"name": r["title"], "url": r["url"], "snippet": r["snippet"]}
                        for r in results
                    ]
                    summary = (results[0]["snippet"] or results[0]["title"]).strip()
                    return {
                        "success": True,
                        "data": {
                            "topic": query_str,
                            "summary": summary or f"Here are the top web results for '{query_str}'.",
                            "sources": sources,
                            "opened_in_browser": top_url
                        },
                        "error": None
                    }
            except Exception:
                pass
            return {
                "success": True,
                "data": {
                    "topic": query_str,
                    "summary": f"No live web results could be fetched for '{query_str}' right now.",
                    "sources": [],
                    "opened_in_browser": None
                },
                "error": None
            }

        url = "https://api.tavily.com/search"
        payload = {
            "api_key": api_key,
            "query": query_str,
            "search_depth": "advanced",
            "include_answer": True
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, timeout=20.0)
                if response.status_code == 200:
                    res_data = response.json()
                    answer = res_data.get("answer") or "Could not compile direct summary answer. Review source links below."
                    results = res_data.get("results", [])
                    
                    sources = []
                    opened_in_browser = None
                    for r in results[:3]:  # Map top 3 sources
                        sources.append({
                            "name": r.get("title", "Web Source"),
                            "url": r.get("url", "https://tavily.com")
                        })
                    # Open the top result page so the user sees the actual answer,
                    # not a search page.
                    if results:
                        opened_in_browser = results[0].get("url")
                        try:
                            import webbrowser
                            webbrowser.open(opened_in_browser)
                        except Exception:
                            pass
                        
                    return {
                        "success": True,
                        "data": {
                            "topic": query_str,
                            "summary": answer,
                            "sources": sources,
                            "opened_in_browser": opened_in_browser
                        },
                        "error": None
                    }
                else:
                    return {"success": False, "error": f"Tavily API returned status: {response.status_code}", "data": {}}
            except Exception as e:
                return {"success": False, "error": f"Failed to complete Tavily search query: {e}", "data": {}}
