"""Text chunking utilities for splitting long text into manageable pieces."""

import re
from typing import List

from .config import MAX_CHARS_PER_CHUNK


def split_text_into_chunks(text: str, max_chars: int = MAX_CHARS_PER_CHUNK) -> List[str]:
    """
    Split long text into chunks based on sentence boundaries.
    
    Args:
        text: The input text to split
        max_chars: Maximum characters per chunk (default from config)
    
    Returns:
        List of text chunks, each not exceeding max_chars
    """
    # Normalize whitespace
    text = " ".join(text.split())
    
    if not text:
        return []
    
    # If text is shorter than max_chars, return as single chunk
    if len(text) <= max_chars:
        return [text]
    
    # Split into sentences using regex
    # This pattern matches sentence endings (. ? !) followed by whitespace
    sentences = re.split(r"(?<=[\.\?\!])\s+", text)
    
    # Filter out empty sentences
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        return [text]
    
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        # If a single sentence exceeds max_chars, we need to split it further
        if len(sentence) > max_chars:
            # If we have accumulated text, save it first
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""
            
            # Split the long sentence by words
            words = sentence.split()
            temp_chunk = ""
            
            for word in words:
                # Check if adding this word would exceed the limit
                potential_chunk = (temp_chunk + " " + word).strip() if temp_chunk else word
                
                if len(potential_chunk) <= max_chars:
                    temp_chunk = potential_chunk
                else:
                    # Save current temp_chunk if it exists
                    if temp_chunk:
                        chunks.append(temp_chunk.strip())
                    temp_chunk = word
            
            # Add remaining temp_chunk
            if temp_chunk:
                current_chunk = temp_chunk
        else:
            # Check if adding this sentence would exceed the limit
            potential_chunk = (current_chunk + " " + sentence).strip() if current_chunk else sentence
            
            if len(potential_chunk) <= max_chars:
                current_chunk = potential_chunk
            else:
                # Save current chunk and start a new one
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
    
    # Add the last chunk if it exists
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    # Filter out empty chunks
    chunks = [chunk for chunk in chunks if chunk]
    
    return chunks if chunks else [text]


