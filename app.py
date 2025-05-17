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
    st.error("No AI models available. Please check your API keys in the .env file.")
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
    # Save the uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
        tmp_file.write(uploaded_file.getbuffer())
        file_path = tmp_file.name
    
    # Process the document
    with st.spinner("Extracting text from document..."):
        try:
            extracted_text, detected_lang = document_processor.extract_text_and_detect_language(file_path, selected_model)
            
            # Show extracted text in a collapsible section
            with st.expander("View Extracted Text"):
                st.text(extracted_text)
            
            # Map language codes to names for display
            language_names = {
                'en': 'English',
                'hi': 'Hindi',
                'ta': 'Tamil',
                'te': 'Telugu',
                'bn': 'Bengali',
                'mr': 'Marathi',
                'gu': 'Gujarati',
                'kn': 'Kannada',
                'ml': 'Malayalam',
                'pa': 'Punjabi',
                'or': 'Odia'
            }
            
            detected_lang_name = language_names.get(detected_lang, 'Unknown')
            st.info(f"Detected language: {detected_lang_name}")
            
            # Ask user for preferred output language
            st.subheader("In which language would you like the final explanation?")
            target_language = st.selectbox(
                "Select language",
                options=list(language_names.values()),
                index=list(language_names.values()).index(detected_lang_name) if detected_lang_name in language_names.values() else 0
            )
            
            # Map language names back to codes
            target_lang_code = {v: k for k, v in language_names.items()}.get(target_language)
            
            # Analyze the legal document
            if st.button("Analyze Document"):
                with st.spinner("Analyzing the legal document..."):
                    # Translate to English if needed for analysis
                    if detected_lang != "en":
                        with st.spinner("Translating document to English for analysis..."):
                            english_text = translator.translate_to_english(extracted_text, detected_lang, selected_model)
                    else:
                        english_text = extracted_text
                    
                    # Add this after extracting text and detecting language
                    print(f"Extracted text length: {len(extracted_text)}")
                    print(f"Detected language: {detected_lang}")
                    
                    # Add this before analyzing the document
                    print(f"Text length for analysis: {len(english_text)}")
                    # Analyze the document
                    analysis = legal_analyzer.analyze_legal_document(english_text, selected_model)
                    
                    # Translate analysis to target language if needed
                    if target_lang_code != "en":
                        with st.spinner(f"Translating analysis to {target_language}..."):
                            final_output = translator.translate_to_language(analysis, "en", target_lang_code, selected_model)
                    else:
                        final_output = analysis
                    
                    # Display the analysis
                    st.markdown("## Legal Analysis")
                    st.markdown(final_output)
                    
                    # Extract win probability if available
                    try:
                        import re
                        win_prob_match = re.search(r'(\d+)%', analysis)
                        if win_prob_match:
                            win_prob = int(win_prob_match.group(1))
                            st.subheader("Case Win Probability")
                            st.progress(win_prob/100)
                            st.metric("Estimated Chance of Success", f"{win_prob}%")
                    except:
                        pass
                        
        except Exception as e:
            st.error(f"Error processing document: {str(e)}")
            
        # Clean up
        try:
            os.remove(file_path)
        except:
            pass

# Footer
st.markdown("---")
st.markdown("⚖️ This is an AI assistant and not a substitute for professional legal advice.")