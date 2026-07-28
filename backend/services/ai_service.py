import requests


OLLAMA_URL = "http://localhost:11434/api/generate"

class AIReviwer:
    
    def ask(self, prompt):

        response = requests.post(
            OLLAMA_URL,

            json={
                "model":"qwen2.5-coder:7b",
                "prompt":prompt,
                "stream":False
            }
        )

        return response.json()["response"]