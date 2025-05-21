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
            extracted_text, detected_lang_from_img = self._process_image_with_ai(file_path, selected_model)
            if detected_lang_from_img == "err_img_proc" or extracted_text is None:
                # Image processing failed
                raise ValueError("Failed to extract text from image. The image might be corrupted or the AI vision model could not process it.")
            
            # The _process_image_with_ai now returns a cleaned language code.
            # We still need a final mapping to ensure consistency and handle any variations.
            img_lang_mapping = {
                'english': 'en', 'en': 'en', 'hindi': 'hi', 'hi': 'hi', 'tamil': 'ta', 'ta': 'ta',
                'telugu': 'te', 'te': 'te', 'bengali': 'bn', 'bn': 'bn', 'marathi': 'mr', 'mr': 'mr',
                'gujarati': 'gu', 'gu': 'gu', 'kannada': 'kn', 'kn': 'kn', 'malayalam': 'ml', 'ml': 'ml',
                'punjabi': 'pa', 'pa': 'pa', 'odia': 'or', 'oriya': 'or', 'or': 'or'
            }
            # Clean the language code received from image processing
            import re
            cleaned_img_lang_code = re.sub(r'[^a-z]', '', detected_lang_from_img.lower())
            final_image_lang_code = img_lang_mapping.get(cleaned_img_lang_code, 'en') # Default to 'en'

            print(f"Language from image processing (raw): '{detected_lang_from_img}', Cleaned: '{cleaned_img_lang_code}', Mapped: '{final_image_lang_code}'")
            return extracted_text, final_image_lang_code

        elif file_extension == '.pdf':
            text = self._extract_from_pdf(file_path)
        elif file_extension in ['.doc', '.docx']:
            text = self._extract_from_word(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
        
        # For non-image files, proceed with language detection using _detect_language_with_ai
        # Ensure text exists and is substantial enough for detection
        if not text or len(text.strip()) < 10: # Minimal length for detection
            print("Text too short or empty for AI language detection, defaulting to 'en'.")
            return text, "en"
            
        text_sample_for_detection = text[:2000] # Use a sample for detection
        lang = self._detect_language_with_ai(text_sample_for_detection, selected_model)
        
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
            
            original_ai_response = detected_lang # Store for logging
            import re
            # Standardize to lowercase and remove non-alpha characters.
            detected_lang_cleaned = re.sub(r'[^a-z]', '', detected_lang.lower())

            # Comprehensive mapping including common names and codes
            lang_mapping = {
                'english': 'en', 'en': 'en',
                'hindi': 'hi', 'hi': 'hi',
                'tamil': 'ta', 'ta': 'ta',
                'telugu': 'te', 'te': 'te',
                'bengali': 'bn', 'bn': 'bn',
                'marathi': 'mr', 'mr': 'mr',
                'gujarati': 'gu', 'gu': 'gu',
                'kannada': 'kn', 'kn': 'kn',
                'malayalam': 'ml', 'ml': 'ml',
                'punjabi': 'pa', 'pa': 'pa',
                'odia': 'or', 'oriya': 'or', 'or': 'or'
            }
            
            final_lang_code = 'en' # Default

            if detected_lang_cleaned in lang_mapping:
                final_lang_code = lang_mapping[detected_lang_cleaned]
            elif len(detected_lang_cleaned) >= 2 and len(detected_lang_cleaned) <= 7: # e.g. 'french' is 6, 'english' is 7
                # This case handles if AI returns a language name not in our specific map,
                # or a valid short code that's not explicitly listed (e.g. 'fr' if prompt allowed it).
                # For this project, we primarily care about mapping to our supported codes.
                # If it's not in lang_mapping, it's effectively unsupported for direct mapping.
                print(f"INFO: Language detection AI returned a code or name '{detected_lang_cleaned}' not in the primary supported list. Raw: '{original_ai_response}'. Defaulting to 'en'.")
                final_lang_code = 'en' # Default to 'en' as it's not in our explicit supported list
            else:
                # Handles very short, very long, or empty strings after cleaning
                print(f"WARNING: Language detection AI returned an unexpected format. Raw response: '{original_ai_response}', Cleaned: '{detected_lang_cleaned}'. Defaulting to 'en'.")
                final_lang_code = 'en'

            print(f"Raw detected language from AI (text): {original_ai_response}")
            print(f"Cleaned AI language response (text): {detected_lang_cleaned}")
            print(f"Final detected language code after mapping (text): {final_lang_code}")
            return final_lang_code
            
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
                    print(f"ERROR: OpenAI vision model (gpt-4-vision-preview) failed: {str(e)}")
                    print("Image processing failed. No text could be extracted via vision model.")
                    return None, "err_img_proc" # Signal error
                
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
                    print(f"ERROR: Gemini vision model (gemini-pro-vision) failed: {str(e)}")
                    print("Image processing failed. No text could be extracted via vision model.")
                    return None, "err_img_proc" # Signal error
            
            # Extract language code and text
            lines = result.split('\n', 1)
            if len(lines) >= 2:
                raw_lang_code_from_vision = lines[0].strip() # Keep original case/format for logging
                extracted_text = lines[1].strip()
                
                # Clean up language code (lowercase, remove non-alpha)
                import re
                # Basic cleaning for the code returned by vision model.
                # The main mapping logic in extract_text_and_detect_language will further refine this.
                lang_code_cleaned_from_vision = re.sub(r'[^a-z]', '', raw_lang_code_from_vision.lower())

                print(f"Raw language output from vision model: '{raw_lang_code_from_vision}', Cleaned: '{lang_code_cleaned_from_vision}'")
                
                # Return the cleaned code; the caller (extract_text_and_detect_language) will perform the final robust mapping.
                return extracted_text, lang_code_cleaned_from_vision
            else:
                # If the vision model output is not as expected (e.g., just text without lang code line)
                print(f"WARNING: Vision model output format unexpected. Raw output: '{result[:200]}...'. Treating all as text, language will be an unverified 'en' or similar code.")
                # Return the full result as text, and a placeholder language code that extract_text_and_detect_language can map.
                return result, "en" # Defaulting to 'en' if format is bad.
                
        except Exception as e:
            print(f"Image processing error during content parsing: {str(e)}")
            # Return None and err_img_proc to signal failure clearly
            return None, "err_img_proc"