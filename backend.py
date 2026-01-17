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

        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config=generation_config
        )

        prompt = f"""
        You are an elite Legal Compliance Officer and Risk Auditor. 
        
        SETTINGS:
        - Strictness Level: {strictness}/10.
        
        Your task: Compare the 'Contract Clause' against the 'Regulation'.
        
        1. Identify specific clauses in the Contract that violate the Regulation.
        2. For each violation, assign a Risk Score (1-10).
        3. ESTIMATE LIABILITY: Based on the regulation (e.g., GDPR fines, breach of contract), estimate the potential financial fine/loss in USD if this is not fixed. Be realistic (e.g., $50,000 - $5,000,000).
        4. REWRITE the clause to be compliant.
        
        Output strictly valid JSON in this structure:
        {{
          "overall_score": 75,
          "total_estimated_liability": 150000,
          "analysis": [
            {{
              "clause_id": "Section X.X",
              "original_text": "The exact text from the contract...",
              "violation": "Explanation of why this violates the regulation...",
              "risk_score": 8,
              "estimated_liability": 50000,
              "suggested_revision": "The compliant version of the text..."
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