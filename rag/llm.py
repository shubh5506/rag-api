from typing import AsyncGenerator
from openai import AsyncOpenAI
from .config import settings

SYSTEM_BASE = """You are an AI portfolio assistant for a sr. software engineer.
Answer using ONLY the provided context snippets from the engineer's resume and project documents.

Rules:
- If the answer is not clearly supported by the context, say: "I don't have that information. Please reach out at sarpal75@gmail.com"
- Do not invent employers, dates, numbers, or tools.
- Be concise and recruiter-friendly: bullets, outcomes, ownership, tech stack.
- Add an 'Evidence' section listing the filenames you used.
"""

def system_prompt(mode: str) -> str:
    if mode == "deep_dive":
        return SYSTEM_BASE + "\nMode: Deep dive. Add architecture and tradeoffs if supported."
    return SYSTEM_BASE + "\nMode: Recruiter. Crisp, skimmable, impact-focused."

_client = None

def get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY missing in .env")
        _client = AsyncOpenAI(api_key=settings.openai_api_key)
    return _client

async def stream_llm_answer(mode: str, message: str, context: str) -> AsyncGenerator[str, None]:
    client = get_client()

    stream = await client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": system_prompt(mode)},
            {"role": "user", "content": f"User question:\n{message}\n\nContext snippets:\n{context}"},
        ],
        temperature=0.2,
        stream=True,
    )

    async for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta




print("=== Recruiter Mode ===")
print(system_prompt("recruiter"))

print("\n=== Deep Dive Mode ===")
print(system_prompt("deep_dive"))