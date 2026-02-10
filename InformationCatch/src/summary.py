import google.generativeai as genai
from openai import OpenAI
import os
import logging
from typing import List, Dict

class NewsSummarizer:
    def __init__(self, provider="openai", model="gpt-4-turbo"):
        self.provider = provider
        self.model = model
        self.client = None

        if self.provider == "openai":
            self.api_key = os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                logging.warning("OPENAI_API_KEY not found.")
            else:
                self.client = OpenAI(api_key=self.api_key)
        
        elif self.provider == "gemini":
            self.api_key = os.getenv("GEMINI_API_KEY")
            if not self.api_key:
                logging.warning("GEMINI_API_KEY not found.")
            else:
                genai.configure(api_key=self.api_key)
                # Gemini client is the module itself + model instance

    def summarize_category(self, category: str, articles: List[Dict]) -> str:
        """
        Summarizes a list of articles/videos for a specific category into a concise bulleted list.
        """
        if not articles:
            return f"No summary available for {category}."

        # Prepare context for LLM
        context = f"Here are the top trending news items for the category: {category}.\n"
        
        for i, art in enumerate(articles[:10], 1):
            title = art.get('title', 'No Title')
            # If transcript is available, use a chunk of it, otherwise use title/summary
            content_snippet = art.get('transcript', '')[:500] if art.get('transcript') else art.get('summary', title)
            context += f"Item {i}: Title: {title}\nContent Snippet: {content_snippet}\n\n"

        prompt = f"""
        You are a professional news editor. I will provide you with raw information about trending videos in the "{category}" sector.
        
        Your task is to summarize the core information into a concise list of key developing stories.
        Each point should extract the "Key Insight" or "New Development".
        
        Format Requirements:
        - Do NOT include links.
        - Do NOT list source names like "CNN" or "TechCrunch".
        - Use Chinese Language strictly.
        - Format as a numbered list.
        - Keep it to exactly the top 5-10 most important points.
        - Style Example:
          1. OpenAI releases new Sora model with improved physics simulation.
          2. Tesla announces breakthrough in 4680 battery production cost reduction.

        Input Data:
        {context}
        """

        try:
            if self.provider == "openai" and self.client:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that summarizes news."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.5
                )
                return response.choices[0].message.content.strip()
            
            elif self.provider == "gemini" and self.api_key:
                model = genai.GenerativeModel(self.model)
                response = model.generate_content(prompt)
                return response.text.strip()
                
            else:
                return "LLM Provider not configured or specific API Key missing."

        except Exception as e:
            logging.error(f"Failed to generate summary for {category}: {e}")
            return "Summary generation failed."

