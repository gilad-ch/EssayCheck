import json
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables.")

client = AsyncOpenAI(api_key=api_key)


async def prompt_llm(prompt: str, system_message: str = None) -> dict:
    if not system_message:
        system_message = "Only reply with the asked description text and nothing else!"

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt},
        ],
        max_tokens=3000,
        response_format={"type": "json_object"},
        temperature=0.7,
    )

    response_content = response.choices[0].message.content.strip()
    return json.loads(response_content)
