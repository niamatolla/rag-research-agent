import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import settings
from openai import OpenAI

client = OpenAI(
    api_key=settings.AZURE_OPENAI_API_KEY,
    base_url=f"{settings.AZURE_OPENAI_ENDPOINT.rstrip('/')}/openai/deployments/{settings.AZURE_OPENAI_CHAT_DEPLOYMENT}",
    default_query={"api-version": settings.AZURE_OPENAI_API_VERSION},
    default_headers={"api-key": settings.AZURE_OPENAI_API_KEY},
)

response =client.chat.completions.create(
    model=settings.AZURE_OPENAI_CHAT_DEPLOYMENT,
    messages=[
        {"role":"system", "content": "Reply with exactly OK"},
        {"role":"user","content": "ping"},
            ],
    max_tokens=10,
)
print(response.choices[0].message.content)