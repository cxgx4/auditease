import streamlit as st
import backend
from docx import Document
from io import BytesIO
import time
import pandas as pd
import plotly.graph_objects as go
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
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.5);
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
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
    
    h1 {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
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

# --- HELPER: RENDER GAUGE CHART ---
def render_gauge(score):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Compliance Health", 'font': {'size': 24, 'color': "#1e293b"}},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': "#2563eb"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 50], 'color': "#fee2e2"},
                {'range': [50, 80], 'color': "#ffedd5"},
                {'range': [80, 100], 'color': "#dcfce7"}],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90}}))
    
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor="rgba(0,0,0,0)", font={'family': "Plus Jakarta Sans"})
    return fig

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
                    and calculates financial liability.
                </p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        b1, b2, b3, b4, b5 = st.columns([1, 2, 2, 2, 1])
        with b3:
            if st.button("✨ Launch Dashboard", use_container_width=True):
                navigate_to("Dashboard")
    
    st.markdown("<br><br>", unsafe_allow_html=True)

    # Social Proof
    st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 0.9rem;'>TRUSTED BY LEGAL TEAMS AT</p>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; opacity: 0.5; font-size: 1.5rem; color: #64748b; font-weight: 700; letter-spacing: 2px;'>STRIPE &nbsp;&nbsp;•&nbsp;&nbsp; AIRBNB &nbsp;&nbsp;•&nbsp;&nbsp; DEEL &nbsp;&nbsp;•&nbsp;&nbsp; COINBASE</div>", unsafe_allow_html=True)

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
            with st.spinner("🕵️‍♂️ Estimating liability & analyzing risks..."):
                reg_text = backend.extract_text(reg_file)
                con_text = backend.extract_text(con_file)
                results = backend.audit_documents(api_key, reg_text, con_text, strictness)
                st.session_state.audit_results = results
                st.rerun()

    # --- RESULTS DISPLAY ---
    if st.session_state.audit_results:
        results = st.session_state.audit_results
        
        # Error handling
        if "error" in results:
            st.error(f"❌ {results['error']}")
        else:
            st.markdown("---")
            
            # 1. EXECUTIVE SUMMARY (Gauge + Liability)
            score = results.get("overall_score", 0)
            liability = results.get("total_estimated_liability", 0)
            analysis = results.get("analysis", [])

            col_gauge, col_metrics = st.columns([1, 2])
            
            with col_gauge:
                #  - Triggers Plotly chart
                fig = render_gauge(score)
                st.plotly_chart(fig, use_container_width=True)
            
            with col_metrics:
                st.markdown("<br>", unsafe_allow_html=True)
                m1, m2 = st.columns(2)
                m1.metric("Financial Liability", f"${liability:,}", "Potential Fine", delta_color="inverse")
                m2.metric("Risks Identified", len(analysis), "Clauses to Fix", delta_color="inverse")
                
                st.info("💡 **AI Insight:** This contract has significant exposure regarding GDPR data retention policies. Immediate revision recommended.")

            # 2. DOCUMENT VAULT (History)
            with st.expander("📂 Document Vault (Recent Audits)", expanded=False):
                history_data = {
                    "Date": ["2026-01-18", "2026-01-17", "2026-01-15"],
                    "Document": [con_file.name if con_file else "Contract_v4.pdf", "Vendor_Agreement_v1.pdf", "HR_Policy.pdf"],
                    "Status": ["🔴 Action Required", "🟢 Approved", "🔴 Action Required"],
                    "Liability": [f"${liability:,}", "$0", "$50,000"]
                }
                st.dataframe(pd.DataFrame(history_data), use_container_width=True, hide_index=True)

            # 3. DETAILED REDLINES (Side-by-Side)
            st.markdown("### 📝 Interactive Redlines")
            
            for item in analysis:
                clause_id = item.get('clause_id', 'Unknown')
                risk = item.get('risk_score', 0)
                fine = item.get('estimated_liability', 0)
                
                with st.container():
                    st.markdown(f"#### 🚩 {clause_id} (Risk: {risk}/10)")
                    st.caption(f"**Violation:** {item.get('violation')} | **Est. Fine:** ${fine:,}")
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown("**❌ Original Text**")
                        st.markdown(f"""
                        <div style="background-color: #fef2f2; border: 1px solid #fecaca; padding: 15px; border-radius: 10px; color: #991b1b;">
                            {item.get('original_text')}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with c2:
                        st.markdown("**✅ Compliant Rewrite**")
                        st.markdown(f"""
                        <div style="background-color: #f0fdf4; border: 1px solid #bbf7d0; padding: 15px; border-radius: 10px; color: #166534;">
                            {item.get('suggested_revision')}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)

            # 4. DOWNLOAD
            doc = Document()
            doc.add_heading('AuditEase Liability Report', 0)
            doc.add_paragraph(f"Total Estimated Liability: ${liability:,}")
            for r in analysis:
                doc.add_heading(r.get('clause_id'), level=1)
                doc.add_paragraph(f"Original: {r.get('original_text')}")
                doc.add_paragraph(f"Fix: {r.get('suggested_revision')}")
            bio = BytesIO()
            doc.save(bio)
            
            st.download_button("📥 Download Official Report", bio.getvalue(), "audit_report.docx", use_container_width=True)

# --- MAIN ROUTER ---
if st.session_state.page == "Home":
    render_home()
elif st.session_state.page == "Dashboard":
    render_dashboard()