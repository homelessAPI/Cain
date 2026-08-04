import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

#for model in client.models.list():
 #   print(model.name)

class AIReviwer:

    def ask_stream(self, prompt):

        stream = client.models.generate_content_stream(
            model="gemini-3.6-flash",
            contents=prompt
        )

        for chunk in stream:

            if chunk.text:
                yield chunk.text