import requests
import json
import time

OLLAMA_URL = "http://localhost:11434/api/generate"


class AIReviwer:

    def ask_stream(self, prompt):
        """
        Generator that yields text chunks as they're produced by Ollama.
        Caller is responsible for consuming it (e.g. via FastAPI's StreamingResponse).
        """
        start = time.time()
        print("sending prompt to AI")

        with requests.post(
            OLLAMA_URL,
            json={
                "model": "qwen2.5-coder:1.5b",
                "prompt": prompt,
                "stream": True,
                "options": {"num_predict": 1000}
            },
            stream=True
        ) as response:
            response.raise_for_status()

            for line in response.iter_lines():
                if not line:
                    continue

                chunk = json.loads(line)

                if chunk.get("response"):
                    yield chunk["response"]

                if chunk.get("done"):
                    break

        print("AI stream finished:", f"{time.time() - start:.2f}s")