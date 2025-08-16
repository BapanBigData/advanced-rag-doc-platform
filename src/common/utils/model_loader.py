
import os
import sys
from dotenv import load_dotenv
from typing import Dict, Any
from src.common.utils.config_loader import load_config
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from src.common.logger.custom_logger import CustomLogger
from src.common.exception.custom_exception import DocumentPortalException

log = CustomLogger().get_logger(__name__)

class ModelLoader:
    
    """
    A utility class to load embedding models and LLM models.
    """
    
    def __init__(self):
        
        load_dotenv()
        self._validate_env()
        self.config = load_config()
        log.info("Configuration loaded successfully", config_keys=list(self.config.keys()))
        
    def _validate_env(self):
        """
        Validate necessary environment variables.
        Ensure API keys exist.
        """
        required_vars = [
            "GROQ_API_KEY",
            "OPENAI_API_KEY"
        ]
        
        self.api_keys={key:os.getenv(key) for key in required_vars}
        missing = [k for k, v in self.api_keys.items() if not v]
        
        if missing:
            log.error("Missing environment variables", missing_vars=missing)
            raise DocumentPortalException("Missing environment variables", sys)
        
        log.info("Environment variables validated", available_keys=[k for k in self.api_keys if self.api_keys[k]])
        
    def load_embeddings(self):
        """
        Load and return the embedding model from config:
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
                    raise ValueError(f"Unsupported embedding provider for this build: {provider}")

                # OpenAI embeddings via LangChain
                # Requires env var: OPENAI_API_KEY
                return OpenAIEmbeddings(model=model_name)

            # (If later you reintroduce Google, add a branch like below)
            # elif "google" in emb_cfg:
            #     cfg = emb_cfg["google"]
            #     model_name = cfg["model_name"]
            #     return GoogleGenerativeAIEmbeddings(model=model_name)

            else:
                raise ValueError("No supported embedding provider block found under 'embedding_model'.")

        except Exception as e:
            log.exception("Error loading embedding model")
            raise DocumentPortalException("Failed to load embedding model", sys) from e
        
    def load_llm(self):
        """
        Load and return the LLM model.
        """
        """Load LLM dynamically based on provider in config."""
        
        llm_block = self.config["llm"]

        log.info("Loading LLM...")
        
        provider_key = os.getenv("LLM_PROVIDER", "openai")  # Default openai
        
        if provider_key not in llm_block:
            log.error("LLM provider not found in config", provider_key=provider_key)
            raise ValueError(f"Provider '{provider_key}' not found in config")

        llm_config = llm_block[provider_key]
        provider = llm_config.get("provider")
        model_name = llm_config.get("model_name")
        temperature = llm_config.get("temperature", 0.2)
        max_tokens = llm_config.get("max_output_tokens", 2048)
        
        log.info("Loading LLM", provider=provider, model=model_name, temperature=temperature, max_tokens=max_tokens)

        if provider == "groq":
            llm=ChatGroq(
                model=model_name,
                api_key=self.api_keys["GROQ_API_KEY"], #type: ignore
                temperature=temperature,
            )
            return llm
            
        elif provider == "openai":
            return ChatOpenAI(
                model=model_name,
                api_key=self.api_keys["OPENAI_API_KEY"],
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