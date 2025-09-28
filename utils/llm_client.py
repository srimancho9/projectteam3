import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class LLMClient:
    def __init__(self, model=None):
        self.client = OpenAI()
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def complete(self, system: str, user: str, max_tokens: int = 800) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.0,
        )
        return resp.choices[0].message.content.strip()
