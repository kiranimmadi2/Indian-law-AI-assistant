import os
from dotenv import load_dotenv
from openai import OpenAI
import google.generativeai as genai

class ModelManager:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Initialize API keys
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        
        # Initialize clients
        self.openai_client = None
        if self.openai_api_key:
            try:
                self.openai_client = OpenAI(api_key=self.openai_api_key)
                print("OpenAI client initialized")
            except Exception as e:
                print(f"Error initializing OpenAI client: {str(e)}")
        
        if self.gemini_api_key:
            try:
                genai.configure(api_key=self.gemini_api_key)
                print("Gemini client initialized")
                self.gemini_available = True
            except Exception as e:
                print(f"Error initializing Gemini client: {str(e)}")
                self.gemini_available = False
        else:
            self.gemini_available = False
    
    def get_available_models(self):
        """Return a list of available models"""
        models = []
        if self.openai_api_key:
            models.append("OpenAI (GPT-3.5)")
        if self.gemini_api_key and self.gemini_available:
            models.append("Google Gemini")
        return models
    
    def get_client(self, model_name):
        """Return the appropriate client based on model name"""
        if "OpenAI" in model_name:
            return self.openai_client, "openai"
        elif "Gemini" in model_name:
            return None, "gemini"  # Gemini uses a different approach
        else:
            raise ValueError(f"Unknown model: {model_name}")