import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)

key = os.getenv("GROQ_API_KEY")

print("Key loaded:", key is not None)
print("Key length:", len(key) if key else 0)
print("Key prefix:", key[:4] if key else "MISSING")


class LLMClient:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        model = os.getenv("GROQ_MODEL")

        if not api_key:
            raise ValueError("GROQ_API_KEY is missing from .env")

        if not model:
            raise ValueError("GROQ_MODEL is missing from .env")

        self.model = model

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )

    def generate(self, messages):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.2
        )

        return response.choices[0].message.content
