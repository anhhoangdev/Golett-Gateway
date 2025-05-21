import os
from typing import Any, Dict, List, Protocol


class EmbeddingFunction(Protocol):
    def __call__(self, texts: List[str]) -> List[List[float]]: ...


class EmbeddingConfigurator:
    def __init__(self):
        self.embedding_functions = {
            "openai": self._configure_openai,
        }

    def configure_embedder(
        self,
        embedder_config: Dict[str, Any]
    ) -> EmbeddingFunction:
        provider = embedder_config.get("provider")
        config = embedder_config.get("config", {})

        if provider not in self.embedding_functions:
            raise Exception(
                f"Unsupported embedding provider: {provider}, supported: {list(self.embedding_functions.keys())}"
            )

        return self.embedding_functions[provider](config)

    @staticmethod
    def _configure_openai(config: Dict[str, Any]) -> EmbeddingFunction:
        import openai

        openai.api_key = config.get("api_key") or os.getenv("OPENAI_API_KEY")
        model = config.get("model", "text-embedding-3-small")

        def embed(texts: List[str]) -> List[List[float]]:
            response = openai.embeddings.create(model=model, input=texts)
            return [d.embedding for d in response.data]

        return embed
