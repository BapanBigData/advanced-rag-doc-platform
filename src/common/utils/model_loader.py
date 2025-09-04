import os
import sys
import json
from dotenv import load_dotenv
from typing import Dict, Any
from src.common.utils.config_loader import load_config
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from src.common.logger.custom_logger import CustomLogger
from src.common.exception.custom_exception import DocumentPortalException

log = CustomLogger().get_logger(__name__)


class ApiKeyManager:
    REQUIRED_KEYS = ["GROQ_API_KEY", "OPENAI_API_KEY"]

    def __init__(self):
        self.api_keys = {}
        raw = os.getenv("advanced_rag_api_keys")

        if raw:
            try:
                parsed = json.loads(raw)
                if not isinstance(parsed, dict):
                    raise ValueError("API_KEYS is not a valid JSON object")
                self.api_keys = parsed
                log.info("Loaded API_KEYS from ECS secret")
            except Exception as e:
                log.warning("Failed to parse API_KEYS as JSON", error=str(e))

        # Fallback to individual env vars
        for key in self.REQUIRED_KEYS:
            if not self.api_keys.get(key):
                env_val = os.getenv(key)
                if env_val:
                    self.api_keys[key] = env_val
                    log.info(f"Loaded {key} from individual env var")

        # Final check
        missing = [k for k in self.REQUIRED_KEYS if not self.api_keys.get(k)]
        
        if missing:
            log.error("Missing required API keys", missing_keys=missing)
            raise DocumentPortalException("Missing API keys", sys)

        log.info(
            "API keys loaded", keys={k: v[:6] + "..." for k, v in self.api_keys.items()}
        )

    def get(self, key: str) -> str:
        val = self.api_keys.get(key)
        if not val:
            raise KeyError(f"API key for {key} is missing")
        return val


class ModelLoader:
    """
    Loads embedding models and LLMs based on config and environment.
    """

    def __init__(self):
        if os.getenv("ENV", "local").lower() != "production":
            load_dotenv()
            log.info("Running in LOCAL mode: .env loaded")
        else:
            log.info("Running in PRODUCTION mode")

        self.api_key_mgr = ApiKeyManager()
        self.config = load_config()
        log.info("YAML config loaded", config_keys=list(self.config.keys()))

    def load_embeddings(self):
        """
        Load and return embedding model from Google Generative AI.
        """
        try:
            log.info("Loading embedding model...")
            emb_cfg: Dict[str, Any] = self.config.get("embedding_model", {})

            # Pick the single provider block present (e.g., "openai")
            if "openai" in emb_cfg:
                cfg = emb_cfg["openai"]
                provider = cfg.get("provider", "openai")
                model_name = cfg["model_name"]

                if provider != "openai":
                    raise ValueError(
                        f"Unsupported embedding provider for this build: {provider}"
                    )

                return OpenAIEmbeddings(
                    model=model_name, api_key=self.api_key_mgr.get("OPENAI_API_KEY")
                )

        except Exception as e:
            log.error("Error loading embedding model", error=str(e))
            raise DocumentPortalException("Failed to load embedding model", sys)

    def load_llm(self):
        """
        Load and return the configured LLM model.
        """
        llm_block = self.config["llm"]
        provider_key = os.getenv("LLM_PROVIDER", "openai")

        if provider_key not in llm_block:
            log.error("LLM provider not found in config", provider=provider_key)
            raise ValueError(f"LLM provider '{provider_key}' not found in config")

        llm_config = llm_block[provider_key]
        provider = llm_config.get("provider")
        model_name = llm_config.get("model_name")
        temperature = llm_config.get("temperature", 0.1)

        log.info("Loading LLM", provider=provider, model=model_name)

        if provider == "groq":
            return ChatGroq(
                model=model_name,
                api_key=self.api_key_mgr.get("GROQ_API_KEY"),  
                temperature=temperature
            )

        elif provider == "openai":
            return ChatOpenAI(
                model=model_name,
                api_key=self.api_key_mgr.get("OPENAI_API_KEY"),
                temperature=temperature
            )

        else:
            log.error("Unsupported LLM provider", provider=provider)
            raise ValueError(f"Unsupported LLM provider: {provider}")


if __name__ == "__main__":
    loader = ModelLoader()

    # Test embedding model loading
    embeddings = loader.load_embeddings()
    print(f"Embedding Model Loaded: {embeddings}")

    # Test the ModelLoader
    result = embeddings.embed_query("Hello, how are you?")
    print(f"Embedding Result: {result}")

    # Test LLM loading based on YAML config
    llm = loader.load_llm()
    print(f"LLM Loaded: {llm}")

    # Test the ModelLoader
    result = llm.invoke("Hello, how are you?")
    print(f"LLM Result: {result.content}")
