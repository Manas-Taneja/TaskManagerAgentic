# ai_task_manager/search_service.py
import os
from typing import List, Dict, Any
import logging
from serpapi import GoogleSearch

logger = logging.getLogger(__name__)

class SearchService:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("SERPAPI_KEY")
        if not self.api_key:
            raise ValueError("SerpAPI key is required. Set SERPAPI_KEY environment variable.")
    
    def search_for_task(self, task_title: str, task_description: str, 
                       resource_types: List[str] = None, num_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for resources related to a task.
        
        Args:
            task_title: Title of the task
            task_description: Description of the task
            resource_types: List of resource types to search for (e.g., ["article", "video", "tool"])
            num_results: Number of results to return
            
        Returns:
            List of resources with title, url, type, and description
        """
        # Build search query from task info
        query = f"{task_title}"
        if task_description:
            # Add key terms from description without making query too long
            query += f" {' '.join(task_description.split()[:10])}"
        
        results = []
        
        # Search for general resources
        general_results = self._perform_search(query, num_results=num_results)
        results.extend(general_results)
        
        # Add specific resource type searches if requested
        if resource_types:
            for res_type in resource_types:
                type_query = f"{query} {res_type}"
                type_results = self._perform_search(
                    type_query, 
                    num_results=max(2, num_results // len(resource_types))
                )
                # Tag these results with the resource type
                for result in type_results:
                    result["type"] = res_type
                
                results.extend(type_results)
        
        # Deduplicate results based on URL
        seen_urls = set()
        unique_results = []
        for result in results:
            if result["url"] not in seen_urls:
                seen_urls.add(result["url"])
                unique_results.append(result)
        
        return unique_results[:num_results]
    
    def _perform_search(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """Perform a search using SerpAPI and format the results."""
        try:
            search_params = {
                "q": query,
                "api_key": self.api_key,
                "num": num_results + 3,  # Request a few extra in case of ads or irrelevant results
            }
            
            search = GoogleSearch(search_params)
            results = search.get_dict()
            
            formatted_results = []
            
            # Process organic results
            if "organic_results" in results:
                for result in results["organic_results"][:num_results]:
                    formatted_result = {
                        "title": result.get("title", ""),
                        "url": result.get("link", ""),
                        "type": "article",  # Default type
                        "description": result.get("snippet", "")
                    }
                    formatted_results.append(formatted_result)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error performing search: {e}")
            return []