from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

def call_llm(prompt: str):
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b:free",
        messages=[
            {"role": "system", "content": "Bạn là một trợ lý thông minh."},
            {"role": "user", "content": prompt}
        ],
        max_tokens = 100000,
        temperature = 0.7
    )
    return response.choices[0].message.content
