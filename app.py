import streamlit as st
import backend
from docx import Document
from io import BytesIO
import time
import pandas as pd
from datetime import datetime

# --- Page Config ---
st.set_page_config(
    page_title="AuditEase AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- GLOBAL STYLES ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .stApp {
        background: radial-gradient(circle at 10% 20%, rgb(242, 246, 252) 0%, rgb(255, 255, 255) 90%);
    }

    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #f0f2f6;
    }

    .glass-card {
        background: rgba(255, 255, 255, 0.6);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.5);
        border-radius: 24px;
        padding: 2rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
    }

    .stButton > button {
        background: #2563eb;
        color: white;
        border-radius: 12px;
        padding: 0.5rem 1rem;
        border: none;
        font-weight: 600;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background: #1d4ed8;
        transform: scale(1.02);
    }
    
    div[data-testid="stHorizontalBlock"] .stButton > button {
        background-color: #f1f5f9;
        color: #0f172a;
    }
    
    h1 {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.02em;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "page" not in st.session_state:
    st.session_state.page = "Home"
if "audit_results" not in st.session_state:
    st.session_state.audit_results = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def navigate_to(page):
    st.session_state.page = page
    st.rerun()

# --- PAGE 1: HOME ---
def render_home():
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 10, 1])
    with c2:
        st.markdown(
            """
            <div style="text-align: center;">
                <div style="display: inline-block; padding: 5px 15px; background: #e0e7ff; color: #3730a3; border-radius: 20px; font-size: 0.8rem; font-weight: 600; margin-bottom: 20px;">
                    🚀 New: AuditEase Enterprise 2.0
                </div>
                <h1 style="font-size: 4.5rem; line-height: 1.1; margin-bottom: 20px;">
                    Compliance Audits.<br>
                    <span style="color: #2563eb; -webkit-text-fill-color: #2563eb;">Done in Seconds.</span>
                </h1>
                <p style="font-size: 1.2rem; color: #64748b; margin-bottom: 40px;">
                    The AI-powered legal engine that reads regulations, checks contracts,<br>
                    and auto-generates redlines. No lawyer required.
                </p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        b1, b2, b3, b4, b5 = st.columns([1, 2, 2, 2, 1])
        with b3:
            if st.button("✨ Launch Dashboard", use_container_width=True):
                navigate_to("Dashboard")
    
    st.markdown("<br><br><br>", unsafe_allow_html=True)

    # Feature Grid
    f1, f2, f3 = st.columns(3)
    with f1:
        st.markdown("""
        <div class="glass-card">
            <h3>⚡ Instant Gaps</h3>
            <p style="color: #64748b">Upload a PDF and find 100% of compliance risks in under 30 seconds.</p>
        </div>
        """, unsafe_allow_html=True)
    with f2:
        st.markdown("""
        <div class="glass-card">
            <h3>🤖 Agentic Reasoning</h3>
            <p style="color: #64748b">Our AI doesn't just match keywords. It understands legal intent and nuance.</p>
        </div>
        """, unsafe_allow_html=True)
    with f3:
        st.markdown("""
        <div class="glass-card">
            <h3>📝 Auto-Redline</h3>
            <p style="color: #64748b">Don't just find the bug. Fix it. We generate compliant clauses automatically.</p>
        </div>
        """, unsafe_allow_html=True)

# --- PAGE 2: DASHBOARD ---
def render_dashboard():
    with st.sidebar:
        st.markdown("### ⚙️ Controls")
        api_key = st.text_input("Gemini API Key", type="password")
        strictness = st.slider("Strictness", 1, 10, 8)
        st.markdown("---")
        if st.button("⬅️ Back to Home"):
            navigate_to("Home")

    st.markdown("## 🛡️ Audit Engine")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("##### 1. The Standard")
        reg_file = st.file_uploader("Regulation PDF", type="pdf", key="reg")
    with c2:
        st.markdown("##### 2. The Contract")
        con_file = st.file_uploader("Contract PDF", type="pdf", key="con")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⚡ Run Compliance Analysis", use_container_width=True):
        if not api_key:
            st.error("Please provide an API Key in the sidebar.")
        elif not reg_file or not con_file:
            st.warning("Please upload both documents.")
        else:
            with st.spinner("🕵️‍♂️ Agents are analyzing legal frameworks..."):
                reg_text = backend.extract_text(reg_file)
                con_text = backend.extract_text(con_file)
                
                # CALL BACKEND with STRICTNESS
                results = backend.audit_documents(api_key, reg_text, con_text, strictness)
                st.session_state.audit_results = results
                st.rerun()

    # --- ERROR HANDLING & RESULTS ---
    if st.session_state.audit_results:
        results = st.session_state.audit_results
        
        # Check for Errors first
        if isinstance(results, list) and len(results) > 0 and "error" in results[0]:
            st.error(f"❌ Analysis Failed: {results[0]['error']}")
            st.info("Tip: Ensure your API key is correct and valid for Gemini 1.5 Flash.")
        
        else:
            st.markdown("---")
            risks = len(results)
            critical = sum(1 for r in results if r.get('risk_score', 0) >= 8)
            
            k1, k2, k3 = st.columns(3)
            k1.metric("Risks Found", risks, delta="-2 from last ver.")
            k2.metric("Critical", critical, delta="Urgent", delta_color="inverse")
            k3.metric("Compliance", f"{100 - (risks*5)}%", "+5%")
            
            tab1, tab2 = st.tabs(["📋 Audit Report", "💬 AI Assistant"])
            
            with tab1:
                for item in results:
                    clause_id = item.get('clause_id', 'Unknown Clause')
                    score = item.get('risk_score', 0)
                    
                    with st.expander(f"🔴 {clause_id} (Risk: {score}/10)"):
                        st.markdown(f"**Violation:** {item.get('violation', 'No details')}")
                        c1, c2 = st.columns(2)
                        c1.error(f"**Original:**\n\n{item.get('original_text', 'N/A')}")
                        c2.success(f"**Fix:**\n\n{item.get('suggested_revision', 'N/A')}")
                
                doc = Document()
                doc.add_heading('AuditEase Report', 0)
                for r in results:
                    doc.add_paragraph(f"Risk: {r.get('clause_id')} | Fix: {r.get('suggested_revision')}")
                bio = BytesIO()
                doc.save(bio)
                st.download_button("📥 Download Report (.docx)", bio.getvalue(), "report.docx")

            with tab2:
                st.info("AI Chat Assistant is ready. (Connect backend logic here)")

# --- MAIN ROUTER ---
if st.session_state.page == "Home":
    render_home()
elif st.session_state.page == "Dashboard":
    render_dashboard()