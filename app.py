import streamlit as st
import backend
from docx import Document
from io import BytesIO
import pandas as pd
import plotly.graph_objects as go

# --- Page Config ---
st.set_page_config(page_title="AuditEase AI", page_icon="🛡️", layout="wide", initial_sidebar_state="collapsed")

# --- COSMIC THEME STYLES ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #ffffff !important;
    }

    /* Cosmic Midnight Background */
    .stApp {
        background: radial-gradient(circle at 50% 10%, #1a1a3a 0%, #050510 100%);
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #050510;
        border-right: 1px solid #6366f133;
    }

    /* Cosmic Glass Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
    }

    /* THE GLARE BUTTON EFFECT */
    .stButton > button {
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%) !important;
        color: white !important;
        border: none !important;
        padding: 12px 24px !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
        box-shadow: 0 0 15px rgba(99, 102, 241, 0.4);
    }

    /* The Animated Glare (Shine) */
    .stButton > button::after {
        content: "";
        position: absolute;
        top: -50%;
        left: -60%;
        width: 20%;
        height: 200%;
        background: rgba(255, 255, 255, 0.4);
        transform: rotate(30deg);
        transition: all 0.5s;
        animation: glare 3s infinite;
    }

    @keyframes glare {
        0% { left: -60%; }
        20% { left: 120%; }
        100% { left: 120%; }
    }

    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 25px rgba(168, 85, 247, 0.6);
    }

    /* Neon Titles */
    h1 {
        background: linear-gradient(to right, #ffffff, #6366f1, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }

    .cosmic-icon {
        background: rgba(99, 102, 241, 0.1);
        border: 1px solid #6366f1;
        width: 70px;
        height: 70px;
        border-radius: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 20px;
        box-shadow: 0 0 20px rgba(99, 102, 241, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "page" not in st.session_state: st.session_state.page = "Home"
if "audit_results" not in st.session_state: st.session_state.audit_results = None

def navigate_to(page):
    st.session_state.page = page
    st.rerun()

# --- GAUGE (Colors remain as original for auditing clarity) ---
def render_gauge(score):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        gauge = {
            'axis': {'range': [0, 100], 'tickcolor': "white"},
            'bar': {'color': "#2563eb"},
            'steps': [
                {'range': [0, 50], 'color': "#fee2e2"},
                {'range': [50, 80], 'color': "#ffedd5"},
                {'range': [80, 100], 'color': "#dcfce7"}]
        }))
    fig.update_layout(height=250, paper_bgcolor="rgba(0,0,0,0)", font={'color': "#ffffff"})
    return fig

# --- PAGE: HOME ---
def render_home():
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, c2, _ = st.columns([1, 8, 1])
    with c2:
        st.markdown(
            """
            <div style="text-align: center;">
                <div class="cosmic-icon"><span style="font-size: 35px;">🛡️</span></div>
                <h1 style="font-size: 4.5rem;">AuditEase <span style="color:#a855f7; -webkit-text-fill-color:#a855f7;">Cosmic Archive</span></h1>
                <p style="font-size: 1.3rem; color: #94a3b8; margin-bottom: 40px;">
                    Turn legal dead-ends into valuable knowledge assets. <br>
                    Making <span style="color:#6366f1;">Invisible Liabilities</span> Visible.
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        _, b_col, _ = st.columns([2, 2, 2])
        with b_col:
            # The button CSS includes the animated glare defined in GLOBAL STYLES
            if st.button("✨ Launch AuditEase", use_container_width=True):
                navigate_to("Dashboard")

# --- PAGE: DASHBOARD ---
def render_dashboard():
    with st.sidebar:
        st.markdown("### ⚙️ Cosmic Controls")
        api_key = st.text_input("Gemini API Key", type="password")
        strictness = st.slider("Strictness", 1, 10, 8)
        if st.button("⬅️ Back to Archive"): navigate_to("Home")

    st.markdown("## 🛡️ Risk Analysis Portal")
    
    col1, col2 = st.columns(2)
    with col1:
        reg_file = st.file_uploader("Upload Regulation", type="pdf")
    with col2:
        con_file = st.file_uploader("Upload Contract", type="pdf")

    if st.button("⚡ Start Neural Audit", use_container_width=True):
        if not api_key: st.error("API Key missing.")
        elif not reg_file or not con_file: st.warning("Documents required.")
        else:
            with st.spinner("Processing through Cosmic Engine..."):
                reg_text = backend.extract_text(reg_file)
                con_text = backend.extract_text(con_file)
                st.session_state.audit_results = backend.audit_documents(api_key, reg_text, con_text, strictness)
                st.rerun()

    if st.session_state.audit_results:
        res = st.session_state.audit_results
        if "error" in res:
            st.error(res["error"])
        else:
            c_g, c_m = st.columns([1, 2])
            with c_g:
                # Gauge stays in standard colors per request
                st.plotly_chart(render_gauge(res.get("overall_score", 0)), use_container_width=True)
            with c_m:
                st.markdown("<br>", unsafe_allow_html=True)
                # Metrics remain in original high-visibility style
                st.metric("Total Financial Liability", f"${res.get('total_estimated_liability', 0):,}", delta="High Risk", delta_color="inverse")
                st.info("💡 Neural Insight: Data privacy clauses violate GDPR Article 17.")

            # Clauses Section
            for item in res.get("analysis", []):
                with st.expander(f"🚩 {item.get('clause_id')} (Risk: {item.get('risk_score')}/10)"):
                    st.write(item.get('violation'))
                    st.success(f"Suggested Revision: {item.get('suggested_revision')}")

# Router
if st.session_state.page == "Home": render_home()
else: render_dashboard()