import fitz  # PyMuPDF
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def extract_text(uploaded_file):
    try:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"

def generate_negotiation_email(api_key, clause_id, violation, suggested_revision):
    if not api_key: return "Error: API Key missing."
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = f"""
        Write a professional negotiation email regarding contract clause: {clause_id}.
        Issue: {violation}
        Required Change: {suggested_revision}
        Tone: Firm but collaborative. Keep it under 150 words.
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

def ask_legal_agent(api_key, query, context_text):
    """
    Answers user questions based on the uploaded document context.
    """
    if not api_key: return "Error: API Key is missing."
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""
        You are an expert Legal Consultant. Answer the question specifically using the provided Context.
        If the answer is not in the text, say "I cannot find that information in the documents."
        
        --- CONTEXT (Regulation & Contract) ---
        {context_text[:50000]} 
        
        --- QUESTION ---
        {query}
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI Error: {str(e)}"

def audit_documents(api_key, regulation_text, contract_text, strictness=8):
    if not api_key: return {"error": "API Key is missing."}
    try:
        genai.configure(api_key=api_key)
        
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config={"response_mime_type": "application/json"}
        )

        prompt = f"""
        Role: Senior Risk Auditor.
        Task: Compare 'Contract' against 'Regulation'.
        Strictness Level: {strictness}/10.
        
        1. Find critical violations (limit to 5 most important).
        2. Assign Risk Score (1-10).
        3. Estimate Financial Liability (USD) based on GDPR/AI Act fines.
        4. Rewrite clause.
        
        Output JSON structure:
        {{
          "overall_score": 75,
          "total_estimated_liability": 150000,
          "analysis": [
            {{
              "clause_id": "Clause 5",
              "original_text": "text from contract...",
              "violation": "why it is wrong...",
              "risk_score": 9,
              "estimated_liability": 50000,
              "suggested_revision": "new text..."
            }}
          ]
        }}

        REGULATION: {regulation_text[:30000]}
        CONTRACT: {contract_text[:30000]}
        """
        response = model.generate_content(prompt)
        return json.loads(response.text)
    except Exception as e:
        return {"error": str(e)}