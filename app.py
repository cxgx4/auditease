import streamlit as st
import backend
from docx import Document
from io import BytesIO
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import os
import time

# --- CONFIGURATION ---
HARDCODED_KEY = os.getenv("GEMINI_API_KEY")

st.set_page_config(
    page_title="AuditEase AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS: COSMIC THEME & ANIMATIONS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Space+Grotesk:wght@300;500;700&display=swap');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
    
    html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif;
        color: #e2e8f0; 
    }

    /* BACKGROUND LAYERS */
    .stApp { background-color: #030712; }

    /* Glowing Stars Animation */
    .stars {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -2;
        background: transparent;
        background-image: 
            radial-gradient(2px 2px at 20px 30px, #eee, rgba(0,0,0,0)),
            radial-gradient(2px 2px at 40px 70px, #fff, rgba(0,0,0,0)),
            radial-gradient(2px 2px at 50px 160px, #ddd, rgba(0,0,0,0)),
            radial-gradient(2px 2px at 90px 40px, #fff, rgba(0,0,0,0));
        background-repeat: repeat; background-size: 200px 200px;
        animation: twinkle 4s infinite; opacity: 0.3;
    }
    @keyframes twinkle { 0% { opacity: 0.3; } 50% { opacity: 0.6; } 100% { opacity: 0.3; } }

    /* Moving Network Mesh */
    .network-bg {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -1;
        background-image: 
            linear-gradient(rgba(99, 102, 241, 0.05) 1px, transparent 1px),
            linear-gradient(90deg, rgba(99, 102, 241, 0.05) 1px, transparent 1px);
        background-size: 40px 40px;
        mask-image: radial-gradient(circle at center, black 40%, transparent 100%);
    }

    /* HERO STYLING */
    .hero-container {
        display: flex; flex-direction: column; align-items: center; text-align: center;
        margin-top: 40px; margin-bottom: 40px;
    }
    h1 {
        font-size: 4.5rem !important; font-weight: 800 !important; letter-spacing: -2px;
        background: linear-gradient(180deg, #fff 0%, #94a3b8 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-shadow: 0 0 30px rgba(139, 92, 246, 0.3);
    }
    .hero-subtitle { font-size: 1.2rem; color: #94a3b8; max-width: 700px; margin: 0 auto; line-height: 1.6; }

    /* GLASS CARDS */
    .glass-card {
        background: linear-gradient(145deg, rgba(17, 24, 39, 0.7), rgba(31, 41, 55, 0.4));
        backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px; padding: 24px; transition: transform 0.3s, border-color 0.3s;
    }
    .glass-card:hover {
        transform: translateY(-5px); border-color: rgba(139, 92, 246, 0.5);
        box-shadow: 0 10px 40px -10px rgba(139, 92, 246, 0.2);
    }

    /* TAGS */
    .tag { padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; }
    .tag-purple { background: rgba(139, 92, 246, 0.2); color: #a78bfa; border: 1px solid rgba(139, 92, 246, 0.3); }
    .tag-blue { background: rgba(56, 189, 248, 0.2); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); }
    .tag-pink { background: rgba(244, 114, 182, 0.2); color: #f472b6; border: 1px solid rgba(244, 114, 182, 0.3); }

    /* NEON BUTTONS */
    .stButton > button {
        background: linear-gradient(90deg, #6366f1, #a855f7); color: white; border: none;
        border-radius: 12px; padding: 0.8rem 2rem; font-weight: 600;
        box-shadow: 0 0 15px rgba(99, 102, 241, 0.4); transition: all 0.3s;
    }
    .stButton > button:hover { box-shadow: 0 0 30px rgba(168, 85, 247, 0.6); transform: scale(1.05); }

    /* UTILS */
    [data-testid="stSidebarNav"] {display: none;}
    .stTextInput input, .stChatInput textarea { background: rgba(15, 23, 42, 0.8) !important; border: 1px solid #334155 !important; color: white !important; }
    .stFileUploader > div > div { background-color: rgba(30, 41, 59, 0.4) !important; border: 2px dashed rgba(99, 102, 241, 0.3) !important; }
</style>

<div class="stars"></div>
<div class="network-bg"></div>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "page" not in st.session_state: st.session_state.page = "Home"
if "audit_results" not in st.session_state: st.session_state.audit_results = None
if "doc_context" not in st.session_state: st.session_state.doc_context = ""
if "chat_history" not in st.session_state: st.session_state.chat_history = []

def navigate_to(page):
    st.session_state.page = page
    st.rerun()

# --- HELPER: GAUGE CHART ---
def render_gauge(score):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = score,
        title = {'text': "Compliance Health", 'font': {'size': 20, 'color': "white"}},
        gauge = {
            'axis': {'range': [0, 100], 'tickcolor': "white"},
            'bar': {'color': "#6366f1"}, 'bgcolor': "rgba(255,255,255,0.05)",
            'steps': [{'range': [0, 50], 'color': "rgba(239, 68, 68, 0.2)"}, {'range': [50, 80], 'color': "rgba(234, 179, 8, 0.2)"}]
        }
    ))
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
    return fig

# ==========================================
# 🏠 PAGE 1: LANDING PAGE (Polished)
# ==========================================
def render_home():
    # Header
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("""<div style="display:flex; align-items:center; gap:12px;"><div style="width:36px; height:36px; background:#6366f1; border-radius:8px; display:flex; align-items:center; justify-content:center; box-shadow:0 0 15px #6366f1;"><i class="fas fa-shield-alt" style="color:white;"></i></div><h3 style="margin:0; font-family:'Space Grotesk'; letter-spacing:1px;">AuditEase AI</h3></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""<div style="text-align:right; color:#94a3b8; font-size:0.9rem;"><span style="color:#4ade80;">● System Online</span></div>""", unsafe_allow_html=True)

    # Hero
    st.markdown("""
    <div class="hero-container">
        <div style="display:inline-block; padding:5px 15px; border:1px solid #6366f1; border-radius:20px; color:#a855f7; font-size:0.8rem; margin-bottom:20px; background:rgba(99,102,241,0.1);">
            ✨ Enterprise Compliance Engine v2.0
        </div>
        <h1>Autonomous Legal<br>Audit Platform</h1>
        <p class="hero-subtitle">
            Transform static contracts into verified knowledge assets. 
            Detect liabilities, calculate fines, and auto-negotiate with Agentic AI.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Action Button
    _, b_col, _ = st.columns([1, 1, 1])
    with b_col:
        if st.button("🚀 Launch Dashboard", use_container_width=True): navigate_to("Dashboard")

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Recent Insights (Interactive)
    st.markdown("""<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;"><h3 style="margin:0;">Recent Activity</h3><span style="color:#94a3b8; cursor:pointer;">View All →</span></div>""", unsafe_allow_html=True)

    g1, g2, g3 = st.columns(3)
    with g1:
        st.markdown("""<div class="glass-card"><div style="display:flex; justify-content:space-between; margin-bottom:15px;"><span class="tag tag-purple">GDPR</span><span style="color:#64748b; font-size:0.8rem;">10m ago</span></div><h4 style="color:white; margin:0 0 10px 0;">Data Retention Breach</h4><p style="color:#94a3b8; font-size:0.9rem;">Clause 4.2 allows indefinite storage.</p></div>""", unsafe_allow_html=True)
    with g2:
        st.markdown("""<div class="glass-card"><div style="display:flex; justify-content:space-between; margin-bottom:15px;"><span class="tag tag-blue">AI ACT</span><span style="color:#64748b; font-size:0.8rem;">1h ago</span></div><h4 style="color:white; margin:0 0 10px 0;">High-Risk System</h4><p style="color:#94a3b8; font-size:0.9rem;">Missing conformity assessment.</p></div>""", unsafe_allow_html=True)
    with g3:
        st.markdown("""<div class="glass-card"><div style="display:flex; justify-content:space-between; margin-bottom:15px;"><span class="tag tag-pink">FINANCE</span><span style="color:#64748b; font-size:0.8rem;">3h ago</span></div><h4 style="color:white; margin:0 0 10px 0;">Liability Cap Breach</h4><p style="color:#94a3b8; font-size:0.9rem;">Cap of $10k is too low.</p></div>""", unsafe_allow_html=True)

# ==========================================
# 📊 PAGE 2: DASHBOARD
# ==========================================
def render_dashboard():
    c1, c2 = st.columns([1, 8])
    with c1: 
        if st.button("⬅️ Home"): navigate_to("Home")
    
    st.markdown("<h1>Compliance Command Center</h1>", unsafe_allow_html=True)
    
    # Uploads
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="glass-card" style="padding:15px; margin-bottom:10px;"><h3 style="margin:0; color:white;">1. The Regulation</h3></div>', unsafe_allow_html=True)
        reg_file = st.file_uploader("", type="pdf", key="reg", label_visibility="collapsed")
    with c2:
        st.markdown('<div class="glass-card" style="padding:15px; margin-bottom:10px;"><h3 style="margin:0; color:white;">2. The Contract</h3></div>', unsafe_allow_html=True)
        con_file = st.file_uploader("", type="pdf", key="con", label_visibility="collapsed")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("⚡ START DEEP AUDIT", use_container_width=True):
        if not reg_file or not con_file:
            st.warning("Please upload both documents.")
        else:
            with st.spinner("🕵️‍♂️ Agents are analyzing liability and legal risks..."):
                reg_text = backend.extract_text(reg_file)
                con_text = backend.extract_text(con_file)
                
                # Save context for Chat
                st.session_state.doc_context = f"REGULATION:\n{reg_text}\n\nCONTRACT:\n{con_text}"
                st.session_state.chat_history = []
                
                results = backend.audit_documents(HARDCODED_KEY, reg_text, con_text)
                st.session_state.audit_results = results
                navigate_to("Results")

    st.divider()
    m1, m2 = st.columns(2)
    with m1:
        st.markdown("""<div class="glass-card"><h4 style="margin:0; color:white;">📚 Regulatory Library</h4></div>""", unsafe_allow_html=True)
        if st.button("Browse Library"): navigate_to("Library")
    with m2:
        st.markdown("""<div class="glass-card"><h4 style="margin:0; color:white;">📈 Risk Analytics</h4></div>""", unsafe_allow_html=True)
        if st.button("View Analytics"): navigate_to("Analytics")

# ==========================================
# 📊 PAGE 3: RESULTS (With Chat!)
# ==========================================
def render_results():
    c1, c2 = st.columns([1, 8])
    with c1: 
        if st.button("⬅️ Back"): navigate_to("Dashboard")
    
    results = st.session_state.audit_results
    if not results or "error" in results:
        st.error(results.get("error", "Unknown error"))
        return

    # Tabs
    tab1, tab2 = st.tabs(["📋 Audit Report", "💬 Chat with Contract"])

    # REPORT TAB
    with tab1:
        score = results.get("overall_score", 0)
        liability = results.get("total_estimated_liability", 0)
        analysis = results.get("analysis", [])

        st.markdown('<div class="glass-card"><h2 style="margin:0; text-align:center; color:white;">Executive Summary</h2></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 2])
        with col1: st.plotly_chart(render_gauge(score), use_container_width=True)
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            m1, m2 = st.columns(2)
            with m1: st.markdown(f"""<div class="glass-card" style="text-align:center;"><h2 style="color:white;">${liability:,.0f}</h2><p>Est. Liability</p></div>""", unsafe_allow_html=True)
            with m2: st.markdown(f"""<div class="glass-card" style="text-align:center;"><h2 style="color:white;">{len(analysis)}</h2><p>Risks Found</p></div>""", unsafe_allow_html=True)

        st.markdown("<h3>Detailed Redlines</h3>", unsafe_allow_html=True)
        for i, item in enumerate(analysis):
            with st.container():
                st.markdown(f"""
                <div class="glass-card">
                    <div style="display:flex; justify-content:space-between;">
                        <h4 style="color:#f87171; margin:0;">🚩 {item.get('clause_id')}</h4>
                        <span class="tag tag-purple">Risk: {item.get('risk_score')}/10</span>
                    </div>
                    <p style="color:#94a3b8; margin-top:10px;"><b>Violation:</b> {item.get('violation')}</p>
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:20px; margin-top:15px;">
                        <div style="background:rgba(239,68,68,0.1); padding:15px; border-radius:12px; border-left:3px solid #ef4444;">
                            <strong style="color:#fca5a5">Original</strong><br>{item.get('original_text')}
                        </div>
                        <div style="background:rgba(34,197,94,0.1); padding:15px; border-radius:12px; border-left:3px solid #22c55e;">
                            <strong style="color:#86efac">Rewrite</strong><br>{item.get('suggested_revision')}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Draft Email #{i+1}", key=f"btn_{i}"):
                    with st.spinner("Drafting..."):
                        email = backend.generate_negotiation_email(HARDCODED_KEY, item.get('clause_id'), item.get('violation'), item.get('suggested_revision'))
                        st.text_area("Draft", email, height=150)

    # CHAT TAB
    with tab2:
        st.markdown("""<div class="glass-card"><h3 style="margin:0; color:white;">🤖 Legal Assistant</h3><p style="color:#94a3b8;">Ask questions about your uploaded documents.</p></div>""", unsafe_allow_html=True)
        
        for msg in st.session_state.chat_history:
            role = "user" if msg["role"] == "user" else "assistant"
            with st.chat_message(role): st.write(msg["content"])

        if prompt := st.chat_input("Ex: What is the termination clause?"):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.write(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("Analyzing documents..."):
                    context = st.session_state.doc_context
                    response = backend.ask_legal_agent(HARDCODED_KEY, prompt, context)
                    st.write(response)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})

# --- PAGE 4 & 5: LIBRARY & ANALYTICS ---
def render_library():
    if st.button("⬅️ Dashboard"): navigate_to("Dashboard")
    st.markdown("<h1>Regulatory Knowledge Base</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown("""<div class="glass-card"><h4 style="color:white">GDPR</h4><p style="color:#94a3b8">EU Data Protection</p></div>""", unsafe_allow_html=True)
    with c2: st.markdown("""<div class="glass-card"><h4 style="color:white">EU AI Act</h4><p style="color:#94a3b8">AI Compliance</p></div>""", unsafe_allow_html=True)
    with c3: st.markdown("""<div class="glass-card"><h4 style="color:white">CCPA</h4><p style="color:#94a3b8">California Privacy</p></div>""", unsafe_allow_html=True)

def render_analytics():
    if st.button("⬅️ Dashboard"): navigate_to("Dashboard")
    st.markdown("<h1>Risk Analytics</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns([2, 1])
    with c1:
        dates = pd.date_range(end=datetime.today(), periods=6, freq='M')
        df = pd.DataFrame({"Date": dates, "Liability": [500000, 450000, 300000, 150000, 100000, 50000]})
        fig = px.area(df, x="Date", y="Liability")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        df_pie = pd.DataFrame({"Cat": ["Privacy", "Security", "Legal"], "Count": [45, 30, 25]})
        fig_pie = px.pie(df_pie, values="Count", names="Cat", hole=0.6)
        fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white", showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)

# --- ROUTER ---
if st.session_state.page == "Home": render_home()
elif st.session_state.page == "Dashboard": render_dashboard()
elif st.session_state.page == "Results": render_results()
elif st.session_state.page == "Library": render_library()
elif st.session_state.page == "Analytics": render_analytics()