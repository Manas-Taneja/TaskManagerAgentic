# ai_task_manager/llm_service.py (Mistral version for Ollama)
import requests
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self, base_url: str = "http://localhost:11434/api/generate", model: str = "mistral"):
        self.base_url = base_url
        self.model = model

    def _generate_response(self, prompt: str) -> str:
        try:
            response = requests.post(self.base_url, json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            })
            response.raise_for_status()
            return response.json().get("response", "No response")
        except Exception as e:
            logger.error(f"Failed to get response from Ollama: {e}")
            return "Unable to generate response at this time."

    def generate_task_insights(self, task: Dict[str, Any], resources: List[Dict[str, Any]]) -> str:
        resources_text = "\n".join([
            f"- {r['title']}: {r['url']}\n  {r['description']}"
            for r in resources
        ])

        prompt = f"""
You are an intelligent task assistant. Summarize and generate insights for:

# Task: {task['title']}
Description: {task['description']}
Status: {task['status']}

Resources:
{resources_text}

Return:
1. Summary of relevant resources (2-3 sentences)
2. Key insights or tips (2-3 points)
3. Next recommended steps

Keep under 200 words.
"""
        return self._generate_response(prompt)

    def generate_daily_digest(self, tasks: List[Dict[str, Any]]) -> str:
        summaries = []
        for task in tasks:
            insight = task.get("insights", [])
            summaries.append(f"- {task['title']} ({task['status']}): {insight[-1]['content'] if insight else 'No insights'}")

        prompt = f"""
You are an AI assistant. Generate a motivational daily task digest with:

- Summary of progress
- Focus areas
- Tips based on recent insights

Tasks:
{chr(10).join(summaries)}

Use markdown.
"""
        return self._generate_response(prompt)
