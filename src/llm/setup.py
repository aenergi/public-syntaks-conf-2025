# src/llm/setup.py
from typing import Optional, Literal, Dict, Any, Union
import os
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.keyvault.secrets import SecretClient
from openai import AsyncAzureOpenAI, AzureOpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Key Vault client
_secret_client = None

# Azure configuration
AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT", None)
AZURE_OPENAI_API_VERSION = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")
AZURE_KEYVAULT_URL = os.environ.get("AZURE_KEYVAULT_URL", None)
AZURE_COGNITIVE_SERVICES = os.environ.get("AZURE_COGNITIVE_SERVICES", "https://cognitiveservices.azure.com/.default")

def get_cognitive_service_token_provider(
    credentials: DefaultAzureCredential = DefaultAzureCredential(),
) -> callable:
    """Get a bearer token provider for Azure Cognitive Services.
    Args:
        credentials (DefaultAzureCredential): Azure credentials to use for authentication.
    Returns:
        callable: A function that returns a bearer token for Azure Cognitive Services.
    """

    return get_bearer_token_provider(
        credentials, AZURE_COGNITIVE_SERVICES
    )

def get_keyvault_client() -> SecretClient:
    """Get or initialize an Azure Key Vault client.
    Returns:
        SecretClient: An instance of the SecretClient for Azure Key Vault.
    """
    global _secret_client
    if _secret_client is None:
        vault_url = os.environ.get("AZURE_KEYVAULT_URL")
        if not vault_url:
            raise ValueError("AZURE_KEYVAULT_URL environment variable must be set")
        _secret_client = SecretClient(vault_url=vault_url, credential=DefaultAzureCredential())
    return _secret_client

def get_secret(secret_name: str, default: Optional[str] = None) -> Optional[str]:
    """Get a secret from Azure Key Vault with fallback to environment variable.
    Args:
        secret_name (str): The name of the secret to retrieve.
        default (Optional[str]): Default value to return if the secret is not found.
    Returns:
        Optional[str]: The value of the secret or the default value.
    """
    try:
        return get_keyvault_client().get_secret(secret_name).value
    except Exception:
        # Fallback to environment variables
        return os.environ.get(secret_name, default)

def create_azure_client(
    azure_endpoint: Optional[str] = AZURE_OPENAI_ENDPOINT,
    api_version: str = AZURE_OPENAI_API_VERSION,
    api_key: Optional[str] = None,
    token_provider: Optional[DefaultAzureCredential] = get_cognitive_service_token_provider(),
    async_mode: bool = True,
) -> Union[AsyncAzureOpenAI, AzureOpenAI]:
    """Create an Azure OpenAI client with the specified configuration.
    Args:
        azure_endpoint (Optional[str]): The Azure OpenAI endpoint.
        api_version (str): The API version to use.
        api_key (Optional[str]): The API key for authentication.
        token_provider (Optional[DefaultAzureCredential]): A function to get a bearer token.
        async_mode (bool): Whether to create an asynchronous client.
    Returns:
        Union[AsyncAzureOpenAI, AzureOpenAI]: An instance of the Azure OpenAI client.
    """
    endpoint = azure_endpoint or get_secret("AZURE_OPENAI_ENDPOINT")
    if not endpoint:
        raise ValueError("Azure OpenAI endpoint must be provided")
    
    if token_provider:
        if async_mode:
            return AsyncAzureOpenAI(
                azure_endpoint=endpoint,
                api_version=api_version,
                azure_ad_token_provider=token_provider,
            )
        else:
            return AzureOpenAI(
                azure_endpoint=endpoint,
                api_version=api_version,
                azure_ad_token_provider=token_provider,
            )
    else:
        key = api_key or get_secret("AZURE_OPENAI_API_KEY")
        if not key:
            raise ValueError("API key must be provided when not using default credentials")
        
        return AsyncAzureOpenAI(
            azure_endpoint=endpoint,
            api_version=api_version,
            api_key=key,
        )