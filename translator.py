import google.generativeai as genai
from model_manager import ModelManager

class Translator:
    def __init__(self):
        # Initialize model manager
        self.model_manager = ModelManager()
    
    def translate_to_english(self, text, source_lang, selected_model="OpenAI (GPT-3.5)"):
        """Translate text from source language to English using selected AI model"""
        # If already English, return as is
        if source_lang == "en":
            return text
            
        client, model_type = self.model_manager.get_client(selected_model)
        
        # Map language codes to full names for better prompting
        lang_names = {
            'hi': 'Hindi',
            'ta': 'Tamil',
            'te': 'Telugu',
            'bn': 'Bengali',
            'mr': 'Marathi',
            'gu': 'Gujarati',
            'kn': 'Kannada',
            'ml': 'Malayalam',
            'pa': 'Punjabi',
            'or': 'Odia',
            'en': 'English'
        }
        
        source_lang_name = lang_names.get(source_lang, source_lang)
        
        try:
            if model_type == "openai":
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": f"You are a professional translator from {source_lang_name} to English. Translate the following text accurately, preserving all information."},
                        {"role": "user", "content": text}
                    ],
                    temperature=0.3,
                    max_tokens=2000
                )
                return response.choices[0].message.content
            
            elif model_type == "gemini":
                gemini_model = genai.GenerativeModel('gemini-pro')
                response = gemini_model.generate_content([
                    f"You are a professional translator from {source_lang_name} to English. Translate the following text accurately, preserving all information.",
                    text
                ])
                return response.text
                
        except Exception as e:
            print(f"Translation error ({source_lang_name} to English): {str(e)}")
            # Instead of returning text:
            raise RuntimeError(f"Translation from {source_lang_name} to English failed. AI service may be unavailable or encountered an issue.") from e
    
    def translate_to_language(self, text, source_lang, target_lang, selected_model="OpenAI (GPT-3.5)"):
        """Translate text from source language to target language using selected AI model"""
        # If source and target are the same, return as is
        if source_lang == target_lang:
            return text
            
        client, model_type = self.model_manager.get_client(selected_model)
        
        # Map language codes to full names for better prompting
        lang_names = {
            'hi': 'Hindi',
            'ta': 'Tamil',
            'te': 'Telugu',
            'bn': 'Bengali',
            'mr': 'Marathi',
            'gu': 'Gujarati',
            'kn': 'Kannada',
            'ml': 'Malayalam',
            'pa': 'Punjabi',
            'or': 'Odia',
            'en': 'English'
        }
        
        source_lang_name = lang_names.get(source_lang, source_lang)
        target_lang_name = lang_names.get(target_lang, target_lang)
        
        try:
            if model_type == "openai":
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": f"You are a professional translator from {source_lang_name} to {target_lang_name}. Translate the following text accurately, preserving all information."},
                        {"role": "user", "content": text}
                    ],
                    temperature=0.3,
                    max_tokens=2000
                )
                return response.choices[0].message.content
            
            elif model_type == "gemini":
                gemini_model = genai.GenerativeModel('gemini-pro')
                response = gemini_model.generate_content([
                    f"You are a professional translator from {source_lang_name} to {target_lang_name}. Translate the following text accurately, preserving all information.",
                    text
                ])
                return response.text
                
        except Exception as e:
            print(f"Translation error ({source_lang_name} to {target_lang_name}): {str(e)}")
            # Instead of returning text:
            raise RuntimeError(f"Translation from {source_lang_name} to {target_lang_name} failed. AI service may be unavailable or encountered an issue.") from e