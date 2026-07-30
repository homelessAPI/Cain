import requests
import time

OLLAMA_URL = "http://localhost:11434/api/generate"

class AIReviwer:
    
    def ask(self, prompt):

        start = time.time()

        print( "sending prompt to AI")
        response = requests.post(
            OLLAMA_URL,

            json={
                "model":"qwen2.5-coder:7b",
                "prompt":prompt,
                "stream":False
            }
        )

        print(
        "AI response received:",
        time.time()-start
    )

        return response.json()["response"]
