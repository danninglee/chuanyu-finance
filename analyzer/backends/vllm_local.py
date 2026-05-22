from openai import OpenAI
from analyzer.backends.base import LLMBackend


class VLLMLocalBackend(LLMBackend):
    def __init__(self, base_url: str = "http://localhost:8000/v1"):
        self.client = OpenAI(api_key="not-needed", base_url=base_url)

    def generate(self, prompt: str, max_tokens: int = 500) -> str:
        response = self.client.chat.completions.create(
            model="Qwen/Qwen2.5-7B-Instruct",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.1,
        )
        return response.choices[0].message.content or ""
