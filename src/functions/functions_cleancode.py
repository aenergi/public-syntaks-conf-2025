#functions to keep the code in notebooks clean

import time
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential
from azure.ai.contentsafety import ContentSafetyClient
from azure.ai.contentsafety.models import AnalyzeTextOptions, TextCategory
from typing import Optional
import os

def remove_soft_hyphens(obj):
    """
    Recursively remove soft hyphens from strings in lists or dictionaries.
    Args:
        obj: The object to process (can be a string, list, or dictionary).
    Returns:
        The object with soft hyphens removed from strings.
    """
    if isinstance(obj, str):
        # Remove soft hyphens from strings
        return obj.replace('\xad', '').replace('\u00ad', '').replace('\N{SOFT HYPHEN}', '')
    elif isinstance(obj, list):
        # Recursively process lists
        return [remove_soft_hyphens(item) for item in obj]
    elif isinstance(obj, dict):
        # Recursively process dictionaries
        return {key: remove_soft_hyphens(value) for key, value in obj.items()}
    return obj  # Return the object as is if it's not a string, list, or dict

def create_embeddings_in_batches(df, llm_client: AzureOpenAI, column_to_embed='description', batch_size=500, dimensions=1024, model='text-embedding-3-large', ) -> dict:
    """
    Create embeddings for each text in the dataframe in batches.
    
    Args:
        df: Pandas DataFrame containing the texts to embed
        column_to_embed: Column name containing the texts to embed
        batch_size: Number of texts to embed in each batch
        dimensions: Dimensions of the embeddings
        model: Model name to use for embeddings
        
    Returns:
        Dictionary mapping index to embedding
    """
    all_embeddings = {}
    total_items = df.shape[0]
    
    # Process in batches to avoid rate limits
    for i in range(0, total_items, batch_size):
        end_idx = min(i + batch_size, total_items)
        print(f"Processing batch {i//batch_size + 1}/{(total_items + batch_size - 1)//batch_size}: items {i} to {end_idx-1}")
        
        # Get texts and their indexes for this batch
        batch_texts = df[column_to_embed].iloc[i:end_idx]
        batch_indexes = batch_texts.index.tolist()
        batch_texts_list = batch_texts.values.tolist()
        
        # Create the embeddings
        try:
            res = llm_client.embeddings.create(input=batch_texts_list, dimensions=dimensions, model=model)
            batch_embeddings = [n.embedding for n in res.data]
            
            # Map embeddings to their respective indexes
            for idx, embedding in zip(batch_indexes, batch_embeddings):
                all_embeddings[idx] = embedding
                
            # Avoid hitting rate limits
            if end_idx < total_items:
                time.sleep(10)
                
        except Exception as e:
            print(f"Error processing batch starting at index {i}: {e}")
            
    print(f"Completed embedding {len(all_embeddings)} out of {total_items} items")
    return all_embeddings

def is_violent(text: str, threshold: float = 0.0, endpoint: Optional[str] = None, credential: Optional[DefaultAzureCredential] = None) -> bool:
    """
    Determines if the given text contains violent content based on Azure Content Safety analysis.

    Args:
        text (str): The text to analyze.
        threshold (float): The severity threshold above which the text is considered violent.
        endpoint (Optional[str]): The Azure Content Safety endpoint. If not provided, it will be fetched from the environment variable `AZURE_CONTENT_SAFETY_ENDPOINT`.
        credential (Optional[DefaultAzureCredential]): Azure credentials for authentication. If not provided, `DefaultAzureCredential` will be used.

    Returns:
        bool: True if the text is considered violent, False otherwise.
    """
    # Use the provided endpoint or fetch it from the environment
    endpoint = endpoint or os.environ.get("AZURE_COGNITIVE_SERVICES")
    if not endpoint:
        raise ValueError("The Azure Content Safety endpoint must be provided or set in the 'AZURE_COGNITIVE_SERVICES' environment variable.")

    # Use the provided credential or default to DefaultAzureCredential
    credential = credential or DefaultAzureCredential()

    try:
        # Initialize the Azure Content Safety client
        client = ContentSafetyClient(endpoint, credential=credential)

        # Analyze the text for violence
        options = AnalyzeTextOptions(text=text, categories=[TextCategory.VIOLENCE])
        response = client.analyze_text(options)

        # Extract severity from the response
        severity = response.categories_analysis[0].severity
        return severity > threshold
    except Exception as e:
        # Log the error and return False as a fallback
        print(f"Error analyzing text for violence: {e}")
        return False