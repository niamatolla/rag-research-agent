from config.settings import settings
from llm.openai_client import OpenAIClient

client = OpenAIClient().get_client()

response =client.chat.completions.create(
    model=settings.AZURE_OPENAI_CHAT_DEPLOYMENT,
    messages=[
        {"role":"system", "content": "Reply with exactly OK"},
        {"role":"user","content": "ping"},
            ],
    max_tokens=10,
)
print(response.choices[0].message.content)