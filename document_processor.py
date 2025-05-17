import os
from PIL import Image
import docx
import PyPDF2
import base64
import google.generativeai as genai
from model_manager import ModelManager

class DocumentProcessor:
    def __init__(self):
        # Initialize model manager
        self.model_manager = ModelManager()
        
    def extract_text_and_detect_language(self, file_path, selected_model="OpenAI (GPT-3.5)"):
        """Extract text from various file formats and detect language"""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        # Extract text based on file type
        if file_extension in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
            # For images, use AI to extract text and detect language
            return self._process_image_with_ai(file_path, selected_model)
        elif file_extension == '.pdf':
            text = self._extract_from_pdf(file_path)
        elif file_extension in ['.doc', '.docx']:
            text = self._extract_from_word(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
        
        # Detect language using AI
        lang = self._detect_language_with_ai(text, selected_model)
        
        return text, lang
    
    def _extract_from_pdf(self, pdf_path):
        """Extract text from PDF"""
        text = ""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
        return text
    
    def _extract_from_word(self, docx_path):
        """Extract text from Word document"""
        doc = docx.Document(docx_path)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    
    def _detect_language_with_ai(self, text, selected_model):
        """Detect language using selected AI model"""
        if not text or len(text.strip()) < 20:
            return "en"  # Default to English for very short texts
            
        # Take a larger sample for better detection
        sample_text = text[:2000]  # Increase sample size
        
        client, model_type = self.model_manager.get_client(selected_model)
        
        try:
            if model_type == "openai":
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a language detection expert. Analyze the following text and respond with ONLY the language code. Valid codes are: en (English), hi (Hindi), ta (Tamil), te (Telugu), bn (Bengali), mr (Marathi), gu (Gujarati), kn (Kannada), ml (Malayalam), pa (Punjabi), or (Odia/Oriya). Respond with ONLY the language code, nothing else."},
                        {"role": "user", "content": sample_text}
                    ],
                    temperature=0.1,  # Lower temperature for more deterministic results
                    max_tokens=10
                )
                detected_lang = response.choices[0].message.content.strip().lower()
            
            elif model_type == "gemini":
                gemini_model = genai.GenerativeModel('gemini-pro')
                response = gemini_model.generate_content([
                    "You are a language detection expert. Analyze the following text and respond with ONLY the language code. Valid codes are: en (English), hi (Hindi), ta (Tamil), te (Telugu), bn (Bengali), mr (Marathi), gu (Gujarati), kn (Kannada), ml (Malayalam), pa (Punjabi), or (Odia/Oriya). Respond with ONLY the language code, nothing else.",
                    sample_text
                ])
                detected_lang = response.text.strip().lower()
            
            # Clean up the response to ensure we get just the language code
            # Remove any non-alphanumeric characters
            import re
            detected_lang = re.sub(r'[^a-z]', '', detected_lang)
            
            # Map to our supported language codes
            lang_mapping = {
                'hindi': 'hi',
                'tamil': 'ta',
                'telugu': 'te',
                'bengali': 'bn',
                'marathi': 'mr',
                'gujarati': 'gu',
                'kannada': 'kn',
                'malayalam': 'ml',
                'punjabi': 'pa',
                'odia': 'or',
                'oriya': 'or',
                'english': 'en',
                'hi': 'hi',
                'ta': 'ta',
                'te': 'te',
                'bn': 'bn',
                'mr': 'mr',
                'gu': 'gu',
                'kn': 'kn',
                'ml': 'ml',
                'pa': 'pa',
                'or': 'or',
                'en': 'en'
            }
            
            # Print for debugging
            print(f"Raw detected language: {detected_lang}")
            
            return lang_mapping.get(detected_lang, 'en')
        except Exception as e:
            print(f"Language detection error: {str(e)}")
            return 'en'  # Default to English if detection fails
    
    def _process_image_with_ai(self, image_path, selected_model):
        """Process image with AI to extract text and detect language"""
        try:
            # Read image file and encode as base64
            with open(image_path, "rb") as image_file:
                b64_image = base64.b64encode(image_file.read()).decode("utf-8")
            
            client, model_type = self.model_manager.get_client(selected_model)
            
            if model_type == "openai":
                # Call OpenAI API with the image
                try:
                    response = client.chat.completions.create(
                        model="gpt-4-vision-preview",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": "Extract all text from this image and identify what language it's in. First line should be just the language code (en, hi, ta, te, bn, mr, gu, kn, ml, pa, or). Then extract all the text."},
                                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}}
                                ]
                            }
                        ],
                        max_tokens=1000
                    )
                    
                    # Parse the response
                    result = response.choices[0].message.content.strip()
                except Exception as e:
                    print(f"OpenAI vision error: {str(e)}")
                    # Fallback to gpt-3.5-turbo if vision model fails
                    print("Falling back to text-only model for language detection")
                    return "", "en"
                
            elif model_type == "gemini":
                # Use Gemini for image processing
                try:
                    gemini_model = genai.GenerativeModel('gemini-pro-vision')
                    response = gemini_model.generate_content([
                        "Extract all text from this image and identify what language it's in. First line should be just the language code (en, hi, ta, te, bn, mr, gu, kn, ml, pa, or). Then extract all the text.",
                        {"mime_type": "image/jpeg", "data": b64_image}
                    ])
                    result = response.text.strip()
                except Exception as e:
                    print(f"Gemini vision error: {str(e)}")
                    return "", "en"
            
            # Extract language code and text
            lines = result.split('\n', 1)
            if len(lines) >= 2:
                lang_code = lines[0].strip().lower()
                extracted_text = lines[1].strip()
                
                # Clean up language code
                import re
                lang_code = re.sub(r'[^a-z]', '', lang_code)
                
                # Map language names/codes to our codes
                lang_mapping = {
                    'hindi': 'hi',
                    'tamil': 'ta',
                    'telugu': 'te',
                    'bengali': 'bn',
                    'marathi': 'mr',
                    'gujarati': 'gu',
                    'kannada': 'kn',
                    'malayalam': 'ml',
                    'punjabi': 'pa',
                    'odia': 'or',
                    'oriya': 'or',
                    'english': 'en',
                    'hi': 'hi',
                    'ta': 'ta',
                    'te': 'te',
                    'bn': 'bn',
                    'mr': 'mr',
                    'gu': 'gu',
                    'kn': 'kn',
                    'ml': 'ml',
                    'pa': 'pa',
                    'or': 'or',
                    'en': 'en'
                }
                
                # Print for debugging
                print(f"Raw detected language from image: {lang_code}")
                
                lang_code = lang_mapping.get(lang_code, 'en')
                return extracted_text, lang_code
            else:
                return result, "en"  # Default to English if format is unexpected
                
        except Exception as e:
            print(f"Image processing error: {str(e)}")
            # Return empty text with English as default
            return "", "en"