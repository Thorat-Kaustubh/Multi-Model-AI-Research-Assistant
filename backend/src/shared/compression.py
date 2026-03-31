import os
from typing import List
from litellm import completion

def compress_text(text: str, query: str = "") -> str:
    """
    Compresses a large block of text into key relevant facts to save tokens for the main reasoning model.
    Uses the 'Fast' model tier (llama-3.1-8b) for high-speed extraction.
    """
    from shared.configuration import BaseConfiguration
    config = BaseConfiguration()
    
    if not text or len(text) < 300:
        return text

    prompt = f"""
    SYSTEM: You are a semantic data compressor.
    TASK: Extract only the critical facts and technical data from the context below that answer: "{query}".
    GOAL: Maximum token savings. Remove all narrative, repetitive headers, and fluff.
    FORMAT: Dense bullet points.
    
    RAW CONTEXT:
    {text[:8000]} # Limit input to prevent compressor rate limits

    COMPRESSED DATA:
    """

    try:
        response = completion(
            model=config.fast_model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0,
            num_retries=2
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Token compression bypassed: {e}")
        return text[:2000] # Fallback to hard truncation
