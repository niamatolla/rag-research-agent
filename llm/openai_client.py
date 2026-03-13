from config.settings import settings
from openai import OpenAI

class OpenAIClient:

    def __init__(self):
        self.client = OpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            base_url=f"{settings.AZURE_OPENAI_ENDPOINT.rstrip('/')}/openai/deployments/{settings.AZURE_OPENAI_CHAT_DEPLOYMENT}",
            default_query={"api-version": settings.AZURE_OPENAI_API_VERSION},
            default_headers={"api-key": settings.AZURE_OPENAI_API_KEY},
                            )

    def get_client(self):
        return self.client