import os
from dotenv import load_dotenv

def load_api_key():
    """Load OpenAI API key from .env file"""
    # Load environment variables from .env file
    load_dotenv()
    
    # Get API key
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError("OpenAI API key not found. Please add it to your .env file.")
    
    return api_key

def load_gemini_api_key():
    """Load Google Gemini API key from .env file"""
    # Load environment variables from .env file
    load_dotenv()
    
    # Get API key
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        raise ValueError("Gemini API key not found. Please add it to your .env file.")
    
    return api_key