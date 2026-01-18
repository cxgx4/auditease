import fitz  # PyMuPDF
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def extract_text(uploaded_file):
    """
    Extracts text from a PDF file object.
    """
    try:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"

def audit_documents(api_key, regulation_text, contract_text, strictness=8):
    """
    Sends texts to Gemini 1.5 Flash for comparison with specific strictness.
    """
    if not api_key:
        return {"error": "API Key is missing. Please check the sidebar."}

    try:
        genai.configure(api_key=api_key)
        
        generation_config = {
            "temperature": 0.1,
            "response_mime_type": "application/json"
        }

        # Updated to a stable model name; change to gemini-1.5-flash if 2.5 is not available
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash", 
            generation_config=generation_config
        )

        prompt = f"""
        You are an elite Legal Compliance Officer and Risk Auditor. 
        Strictness Level: {strictness}/10.
        
        Task: Compare Contract vs Regulation. Identify violations, risk scores (1-10), 
        and estimate financial liability in USD.
        
        Output strictly valid JSON:
        {{
          "overall_score": 75,
          "total_estimated_liability": 150000,
          "analysis": [
            {{
              "clause_id": "Section X.X",
              "original_text": "...",
              "violation": "...",
              "risk_score": 8,
              "estimated_liability": 50000,
              "suggested_revision": "..."
            }}
          ]
        }}

        --- REGULATION ---
        {regulation_text[:30000]} 
        
        --- CONTRACT ---
        {contract_text[:30000]}
        """

        response = model.generate_content(prompt)
        result = json.loads(response.text)
        return result
        
    except Exception as e:
        return {"error": f"Backend Error: {str(e)}"}