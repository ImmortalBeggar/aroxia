import os
import google.generativeai as genai
from llama_cpp import Llama
import requests
from bs4 import BeautifulSoup

class Brain:
    def __init__(self, api_key=None, local_model_path=None):
        self.api_key = api_key
        self.local_model_path = local_model_path
        self.use_local = False
        
        if api_key:
            genai.configure(api_key=api_key)
            # Use tools for search and web scraping
            self.model = genai.GenerativeModel(
                'gemini-1.5-pro',
                tools=[self.google_search_tool, self.web_scraper_tool]
            )
        else:
            self.use_local = True
            self._init_local_model()

    def google_search_tool(self, query: str):
        """Search Google for the latest news or specific information."""
        # This is a placeholder for actual API integration (e.g., Serper or Google Custom Search)
        return f"Search results for '{query}': [Link 1], [Link 2]. (Simulated)"

    def web_scraper_tool(self, url: str):
        """Fetch and extract text content from a given URL."""
        try:
            res = requests.get(url, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            return soup.get_text()[:2000] # Return first 2000 chars
        except Exception as e:
            return f"Error fetching URL: {e}"

    def _init_local_model(self):
        if self.local_model_path and os.path.exists(self.local_model_path):
            self.llm = Llama(model_path=self.local_model_path, n_ctx=2048)
        else:
            print("Local model not found. Running in dummy mode.")
            self.llm = None

    async def generate_response(self, prompt, context="", image=None):
        if not self.use_local:
            try:
                # Enable automatic function calling
                chat = self.model.start_chat(enable_automatic_function_calling=True)
                full_prompt = f"Context: {context}\n\nUser: {prompt}"
                
                if image:
                    response = chat.send_message([full_prompt, image])
                else:
                    response = chat.send_message(full_prompt)
                return response.text
            except Exception as e:
                print(f"Gemini Error: {e}. Switching to local.")
                self.use_local = True
        
        if self.use_local and self.llm:
            output = self.llm(f"Q: {prompt} A: ", max_tokens=128, stop=["Q:", "\n"], echo=True)
            return output['choices'][0]['text']
        
        return "I'm having trouble thinking right now. Maybe I'm offline?"

    def toggle_mode(self):
        self.use_local = not self.use_local
        return "Local Mode" if self.use_local else "Cloud Mode"
