import streamlit as st
import os
import tempfile
from document_processor import DocumentProcessor
from translator import Translator
from legal_analyzer import LegalAnalyzer
from model_manager import ModelManager

# Create temp directory if it doesn't exist
os.makedirs("temp", exist_ok=True)

# Initialize components
model_manager = ModelManager()
document_processor = DocumentProcessor()
translator = Translator()
legal_analyzer = LegalAnalyzer()

# Set page config
st.set_page_config(
    page_title="Indian Legal AI Assistant",
    page_icon="⚖️",
    layout="wide"
)

# App title
st.title("🇮🇳 Indian Legal AI Assistant")
st.subheader("Upload legal documents and get analysis in your language")

# Get available models
available_models = model_manager.get_available_models()

if not available_models:
    error_messages = []
    # Check for presence of keys first
    if not model_manager.openai_api_key:
        error_messages.append("OpenAI API key is missing.")
    elif not model_manager.is_openai_available():
        error_messages.append("OpenAI API key found, but client failed to initialize. Please check if the key is valid and active.")

    if not model_manager.gemini_api_key:
        error_messages.append("Google Gemini API key is missing.")
    elif not model_manager.is_gemini_available():
        error_messages.append("Google Gemini API key found, but client failed to initialize. Please check if the key is valid and active.")
    
    if not model_manager.openai_api_key and not model_manager.gemini_api_key:
            st.error("CRITICAL: No AI models are available because API keys for both OpenAI and Google Gemini are missing. Please create a `.env` file in the project root (you can copy from `.env.example`) and add your API keys. The application cannot function without at least one valid API key.")
    elif error_messages:
        st.error("AI Model Initialization Issues:\n" + "\n".join(error_messages) + "\nPlease create/check your `.env` file (use `.env.example` as a template) and ensure your API keys are correct and active. The application may have limited or no functionality until this is resolved.")
    else:
        # This case should ideally not be hit if logic is correct, but as a fallback:
        st.error("No AI models available. Please check your API key configuration in the .env` file (use `.env.example` as a template).")
    st.stop()

# Model selection
selected_model = st.sidebar.selectbox(
    "Select AI Model",
    options=available_models,
    index=0
)

st.sidebar.info(f"Using {selected_model} for analysis")

# File uploader
uploaded_file = st.file_uploader("Upload your legal document", 
                                type=["pdf", "docx", "jpg", "jpeg", "png"])

if uploaded_file is not None:
    file_path = None  # Initialize file_path
    try:
        # Save the uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
            tmp_file.write(uploaded_file.getbuffer())
            file_path = tmp_file.name
        
        # Process the document
        with st.spinner("Extracting text from document..."):
            # Note: The main processing logic is now within this try block.
            # Errors from document_processor, translator, legal_analyzer will be caught by the outer except blocks.
            extracted_text, detected_lang = document_processor.extract_text_and_detect_language(file_path, selected_model)
            
            with st.expander("View Extracted Text"):
                st.text(extracted_text)
            
            language_names = {
                'en': 'English', 'hi': 'Hindi', 'ta': 'Tamil', 'te': 'Telugu',
                'bn': 'Bengali', 'mr': 'Marathi', 'gu': 'Gujarati', 'kn': 'Kannada',
                'ml': 'Malayalam', 'pa': 'Punjabi', 'or': 'Odia'
            }
            detected_lang_name = language_names.get(detected_lang, 'Unknown')
            st.info(f"Detected language: {detected_lang_name}")
            
            st.subheader("In which language would you like the final explanation?")
            target_language = st.selectbox(
                "Select language",
                options=list(language_names.values()),
                index=list(language_names.values()).index(detected_lang_name) if detected_lang_name in language_names.values() else 0
            )
            target_lang_code = {v: k for k, v in language_names.items()}.get(target_language)
            
            if st.button("Analyze Document"):
                with st.spinner("Analyzing the legal document..."): # This spinner might be nested if translation happens
                    if detected_lang != "en":
                        with st.spinner("Translating document to English for analysis..."):
                            english_text = translator.translate_to_english(extracted_text, detected_lang, selected_model)
                    else:
                        english_text = extracted_text
                    
                    print(f"Extracted text length: {len(extracted_text)}")
                    print(f"Detected language: {detected_lang}")
                    print(f"Text length for analysis: {len(english_text)}")
                    
                    analysis = legal_analyzer.analyze_legal_document(english_text, selected_model)
                    
                    if target_lang_code != "en":
                        with st.spinner(f"Translating analysis to {target_language}..."):
                            final_output = translator.translate_to_language(analysis, "en", target_lang_code, selected_model)
                    else:
                        final_output = analysis
                    
                    st.markdown("## Legal Analysis")
                    st.markdown(final_output)
                    
                    try:
                        import re
                        win_prob_match = re.search(r"Win Probability: (\d+)%", analysis, re.IGNORECASE)
                        if win_prob_match:
                            win_prob = int(win_prob_match.group(1))
                            st.subheader("Case Win Probability")
                            st.progress(win_prob / 100.0)
                            st.metric("Estimated Chance of Success", f"{win_prob}%")
                        elif "Win Probability: Not determinable" in analysis:
                            st.subheader("Case Win Probability")
                            st.info("The AI could not determine a specific win probability for this case.")
                    except Exception as e_prob:
                        print(f"Error processing win probability: {e_prob}")
                        pass

    except ValueError as ve: # Catch specific ValueErrors from document_processor
        st.error(f"Document processing issue: {str(ve)}")
    except RuntimeError as re: # Catch RuntimeErrors from translator or analyzer
        st.error(f"Application runtime error: {str(re)}")
    except Exception as e: # General catch-all for other unexpected errors
        st.error(f"An unexpected error occurred: {str(e)}")
        # For debugging, you might want to log the full traceback:
        # import traceback
        # print(traceback.format_exc())
            
    finally:
        # Clean up
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"Successfully removed temp file: {file_path}")
            except Exception as e_remove:
                print(f"Error removing temp file {file_path}: {str(e_remove)}")
                st.warning(f"Could not remove temporary file: {file_path}. It may need to be manually deleted.")

# Footer
st.markdown("---")
st.markdown("⚖️ This is an AI assistant and not a substitute for professional legal advice.")