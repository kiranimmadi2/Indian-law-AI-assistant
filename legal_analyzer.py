import google.generativeai as genai
from model_manager import ModelManager

class LegalAnalyzer:
    def __init__(self):
        # Initialize model manager
        self.model_manager = ModelManager()
    
    def analyze_legal_document(self, text, selected_model="OpenAI (GPT-3.5)"):
        """Analyze legal document using the selected AI model"""
        client, model_type = self.model_manager.get_client(selected_model)
        
        # Check if text is too large and truncate if necessary
        max_length = 4000  # Set a reasonable limit
        if len(text) > max_length:
            print(f"Warning: Text is too large ({len(text)} chars). Truncating to {max_length} chars.")
            # Take the first part and the last part to capture important information
            first_part = text[:max_length//2]
            last_part = text[-max_length//2:]
            text = first_part + "\n...[Content truncated due to length]...\n" + last_part
        
        prompt = """You are an Indian legal advisor. Analyze the provided legal document and provide a comprehensive analysis with the following sections:

1. 🧾 Case Summary: Explain what the case is about in simple language.
2. 📜 Relevant Laws: List the relevant laws, sections, and precedents that apply to this case.
3. 💡 Legal Advice: Provide practical advice for a common person dealing with this legal matter.
4. 📈 Win Probability: Estimate the chance of winning this case (as a percentage) based on the information provided.

Note: The document may be truncated due to length. Focus on analyzing the visible portions."""
        
        try:
            if model_type == "openai":
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo-16k",  # Use a model with larger context window if available
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": text}
                    ],
                    temperature=0.5,
                    max_tokens=2000
                )
                return response.choices[0].message.content
            
            elif model_type == "gemini":
                gemini_model = genai.GenerativeModel('gemini-pro')
                response = gemini_model.generate_content([
                    prompt,
                    text
                ])
                return response.text
            
        except Exception as e:
            print(f"Legal analysis error: {str(e)}")
            return f"Error analyzing document: {str(e)}"