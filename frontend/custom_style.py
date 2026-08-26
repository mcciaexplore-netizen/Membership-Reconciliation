import streamlit as st

def inject_custom_css():
    st.markdown("""
<style>
    .main { background-color: #f5f7fa; }
    [data-testid="stMetric"] { 
        background: white; 
        border-radius: 12px; 
        padding: 16px; 
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid #1a237e;
    }
    [data-testid="stMetricValue"] { font-size: 28px !important; font-weight: 700; }
    [data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }
    [data-testid="stFileUploader"] {
        background: white;
        border: 2px dashed #1a237e;
        border-radius: 12px;
        padding: 24px;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background: white;
        border-radius: 8px 8px 0 0;
        padding: 12px 24px;
        font-weight: 600;
        border: 1px solid #e0e0e0;
        border-bottom: none;
    }
    .stTabs [aria-selected="true"] { background: #1a237e !important; color: white !important; border-color: #1a237e; }
    
    /* Better header styling */
    h1, h2, h3 {
        font-family: 'Inter', 'Roboto', sans-serif;
        color: #1a237e;
    }
</style>
""", unsafe_allow_html=True)
