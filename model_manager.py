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
        self.openai_client_initialized = False
        if self.openai_api_key:
            try:
                self.openai_client = OpenAI(api_key=self.openai_api_key)
                print("OpenAI client initialized successfully.")
                self.openai_client_initialized = True # Set status
            except Exception as e:
                print(f"Error initializing OpenAI client: {str(e)}")
                self.openai_client_initialized = False
        
        self.gemini_client_initialized = False
        if self.gemini_api_key:
            try:
                genai.configure(api_key=self.gemini_api_key)
                # Test with a simple call if necessary, or rely on configure success
                # For simplicity, we'll assume configure() is enough for now.
                # To be more robust, you could add a lightweight test call.
                print("Gemini client initialized successfully.")
                self.gemini_client_initialized = True # Set status
            except Exception as e:
                print(f"Error initializing Gemini client: {str(e)}")
                self.gemini_client_initialized = False
    
    # New methods
    def is_openai_available(self):
        return self.openai_client is not None and self.openai_client_initialized

    def is_gemini_available(self):
        # Gemini's genai module is configured globally, so check initialization status
        return self.gemini_api_key is not None and self.gemini_client_initialized # check status

    def get_available_models(self):
        models = []
        if self.is_openai_available():
            models.append("OpenAI (GPT-3.5)")
        if self.is_gemini_available():
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