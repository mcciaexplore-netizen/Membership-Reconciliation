"""Streamlit frontend for Membership Reconciliation Engine — Premium UI."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.ingest import load_backend_data, load_bank_statement, load_config
from src.matcher import reconcile
from src.reporter import write_report

# ─── Page Config ───
st.set_page_config(
    page_title="Membership Reconciliation | MCCIA",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * { font-family: 'Inter', sans-serif !important; }
    
    .main { background-color: #f8fafc !important; }
    
    /* Layout Spacing Fixes */
    [data-testid="stAppViewBlockContainer"],
    .block-container,
    [data-testid="stSidebarContent"],
    [data-testid="stSidebarUserContent"] {
        padding-top: 1rem !important;
    }
    header[data-testid="stHeader"],
    [data-testid="stSidebarHeader"] {
        display: none !important;
    }
    
    /* Dark Sidebar */
    [data-testid="stSidebar"] {
        background-color: #111827 !important;
        border-right: none;
    }
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown {
        color: #f1f5f9 !important;
    }
    
    /* Primary Run Button */
    [data-testid="stSidebar"] .stButton button {
        background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%) !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        border: none !important;
        padding: 10px 24px !important;
        width: 100% !important;
        transition: all 0.2s !important;
        box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.4);
    }
    [data-testid="stSidebar"] .stButton button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 12px -2px rgba(59, 130, 246, 0.5);
    }
    
    /* File Uploader fixes */
    [data-testid="stSidebar"] [data-testid="stFileUploader"] > label {
        color: white !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        margin-bottom: 8px !important;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
        border: 1px dashed #475569 !important;
        border-radius: 12px !important;
        background: #1e293b !important;
        padding: 24px !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        transition: all 0.2s !important;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"]:hover {
        border-color: #3b82f6 !important;
        background: #273549 !important;
    }
    
    /* Hide native button and 'Drag and drop' span entirely */
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button,
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] > div > span,
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] > span {
        display: none !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        width: 100% !important;
    }
    
    /* Inject 'Upload' text */
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"]::before {
        content: "☁️ Upload";
        display: block !important;
        color: white !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        margin-bottom: 8px !important;
        text-align: center !important;
    }
    
    /* Small description */
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] small {
        display: block !important;
        color: #94a3b8 !important;
        font-size: 11px !important;
        text-align: center !important;
    }
    
    /* Uploaded File Item (when a file is successfully loaded) */
    [data-testid="stSidebar"] [data-testid="stUploadedFile"] {
        background: #1e293b !important;
        border: 1px solid #374151 !important;
        border-radius: 8px !important;
        color: white !important;
    }
    [data-testid="stSidebar"] [data-testid="stUploadedFile"] * {
        color: white !important;
    }
    
    /* KPI Cards */
    .kpi-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02), 0 4px 12px rgba(0,0,0,0.03);
        transition: all 0.2s;
        height: 100%;
        display: flex;
        flex-direction: column;
    }
    .kpi-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 8px;
    }
    .kpi-icon-img {
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
    }
    .kpi-value {
        font-size: 28px;
        font-weight: 700;
        color: #0f172a;
        line-height: 1.2;
    }
    .kpi-label {
        font-size: 11px;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 4px;
    }
    .kpi-trend {
        font-size: 12px;
        font-weight: 500;
        margin-top: auto;
        padding: 4px 8px;
        border-radius: 4px;
        display: inline-block;
        width: fit-content;
    }
    
    /* Section Headers */
    .section-header {
        font-size: 18px;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    /* Chart Containers */
    .chart-container {
        background: white;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02), 0 4px 12px rgba(0,0,0,0.03);
        height: 100%;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 16px;
        background: transparent;
        padding: 0px;
        border-radius: 0px;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 20px;
        padding: 6px 16px;
        font-weight: 600;
        font-size: 14px;
        color: #64748b;
        border: none;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #0f172a;
        background: white;
    }
    .stTabs [aria-selected="true"] {
        background: white !important;
        color: #0f172a !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
    }
    
    /* Data Tables */
    .stDataFrame {
        border-radius: 8px !important;
        overflow: hidden !important;
        border: 1px solid #e2e8f0 !important;
    }
    .stDataFrame thead tr th {
        background: #f1f5f9 !important;
        color: #475569 !important;
        font-weight: 600 !important;
        font-size: 11px !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        padding: 10px 16px !important;
    }
    .stDataFrame tbody tr:nth-child(even) {
        background: white !important;
    }
    .stDataFrame tbody tr:hover {
        background: #f8fafc !important;
    }
    
    /* Download Buttons */
    .download-btn button {
        background: #111827 !important;
        color: white !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
        padding: 8px 16px !important;
        border: none !important;
        font-size: 13px !important;
    }
    .download-btn button:hover {
        background: #374151 !important;
    }
    
    /* Status Badges */
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }
    .badge-matched { background: #dcfce7; color: #166534; }
    .badge-unmatched { background: #fee2e2; color: #991b1b; }
    .badge-partial { background: #fef3c7; color: #92400e; }
    .badge-duplicate { background: #dbeafe; color: #1e40af; }
    
    /* Empty State */
    .empty-state {
        text-align: center;
        padding: 60px 20px;
        color: #94a3b8;
    }
    .empty-state-icon {
        font-size: 64px;
        margin-bottom: 16px;
        opacity: 0.5;
    }
    
    /* Divider */
    hr {
        border: none;
        height: 1px;
        background: #e2e8f0;
        margin: 24px 0;
    }
</style>
""", unsafe_allow_html=True)

# ─── Sidebar ───
with st.sidebar:
    st.markdown("""
    <div style="padding: 10px 0 30px 0;">
        <h1 style="font-size: 24px; font-weight: 700; margin: 0; color: white;">🏛️ MCCIA</h1>
        <p style="font-size: 13px; color: #94a3b8; margin: 4px 0 0 0;">Membership Reconciliation</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown('<p style="font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; margin-bottom: 16px;">📁 Upload Files</p>', unsafe_allow_html=True)
    
    bank_file = st.file_uploader(
        "Bank Statement (CSV / Excel)",
        type=["csv", "xlsx", "xls"],
        key="bank",
        help="Upload your bank statement or payment summary file"
    )
    
    backend_file = st.file_uploader(
        "Backend Membership Data (CSV / Excel)",
        type=["csv", "xlsx", "xls"],
        key="backend",
        help="Upload your Tally ledger or backend invoice file"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    run_clicked = st.button("🚀 Run Reconciliation", use_container_width=True, type="primary")
    
    st.markdown("---")
    
    st.markdown("""
    <div style="padding: 16px; background: #1e293b; border-radius: 12px; margin-top: 20px;">
        <p style="font-size: 12px; color: #94a3b8; margin: 0 0 8px 0;">💡 Tip</p>
        <p style="font-size: 13px; color: #cbd5e1; margin: 0; line-height: 1.5;">
            Files are matched on <b>MBK booking numbers</b>. Ensure both files contain the <code>bk_no</code> or <code>Voucher Ref. No.</code> column.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ─── Main Content ───
st.markdown("""
<div style="padding: 10px 0 30px 0;">
    <h1 style="font-size: 32px; font-weight: 700; color: #0f172a; margin: 0;">Membership Reconciliation</h1>
    <p style="font-size: 15px; color: #64748b; margin: 8px 0 0 0;">
        Compare bank collections against backend membership invoices. Identify matched, unmatched, and discrepant records.
    </p>
</div>
""", unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def load_dataframes(bank_bytes, backend_bytes, bank_name, backend_name):
    config = load_config(ROOT / "config" / "config.yaml")
    tmp_dir = ROOT / "frontend" / "tmp_uploads"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    
    bank_ext = Path(bank_name).suffix
    backend_ext = Path(backend_name).suffix
    
    bank_path = tmp_dir / f"uploaded_bank{bank_ext}"
    backend_path = tmp_dir / f"uploaded_backend{backend_ext}"
    
    bank_path.write_bytes(bank_bytes)
    backend_path.write_bytes(backend_bytes)
    
    bank_df = load_bank_statement(bank_path, config)
    backend_df = load_backend_data(backend_path, config)
    return bank_df, backend_df, config


def render_kpi_card(icon, value, label, subtitle, trend=None, trend_color=None, top_border_color="#e2e8f0", icon_bg="white", icon_color="#000"):
    trend_html = ""
    if trend:
        trend_html = f'<div class="kpi-trend" style="background: {trend_color}20; color: {trend_color};">{trend}</div>'
    
    return f"""
    <div class="kpi-card" style="border-top: 4px solid {top_border_color}; border-left: none;">
        <div class="kpi-header">
            <div class="kpi-icon-img" style="background: {icon_bg}; color: {icon_color};">{icon}</div>
            <div class="kpi-value">{value}</div>
        </div>
        <div style="font-size: 13px; font-weight: 700; color: #111827; margin-top: 8px;">{label}</div>
        <div style="font-size: 13px; color: #6b7280; margin-bottom: 12px;">{subtitle}</div>
        {trend_html}
    </div>
    """


def render_kpis(summary: dict):
    match_rate = round((summary["matched_count"] / max(summary["matched_count"] + summary["unmatched_bank_count"] + summary["unmatched_backend_count"], 1)) * 100, 1)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(render_kpi_card(
            "🏦", f"₹{summary['total_bank_amount']:,.0f}", "TOTAL BANK AMOUNT", "Total collections",
            f"↑ {match_rate}% matched", "#10b981", top_border_color="#3b82f6", icon_color="#3b82f6"
        ), unsafe_allow_html=True)
    with col2:
        st.markdown(render_kpi_card(
            "📋", f"₹{summary['total_backend_amount']:,.0f}", "TOTAL BACKEND AMOUNT", "Invoiced value",
            None, None, top_border_color="#8b5cf6", icon_color="#8b5cf6"
        ), unsafe_allow_html=True)
    with col3:
        variance_color = "#ef4444" if summary['variance'] != 0 else "#10b981"
        variance_icon = "⚠️" if summary['variance'] != 0 else "✅"
        st.markdown(render_kpi_card(
            variance_icon, f"₹{abs(summary['variance']):,.0f}", "VARIANCE", "Difference in total value",
            "Needs attention" if summary['variance'] != 0 else "Fully reconciled", variance_color, top_border_color=variance_color, icon_color=variance_color
        ), unsafe_allow_html=True)
    with col4:
        st.markdown(render_kpi_card(
            "🎯", str(summary['matched_count']), "MATCHED RECORDS", "Successfully reconciled",
            f"{match_rate}% success rate", "#10b981", top_border_color="#10b981", icon_color="#10b981"
        ), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col5, col6, col7, col8 = st.columns(4)
    with col5:
        st.markdown(render_kpi_card(
            "🔴", str(summary['unmatched_bank_count']), "UNMATCHED BANK", "No invoice found",
            None, None, top_border_color="#ef4444"
        ), unsafe_allow_html=True)
    with col6:
        st.markdown(render_kpi_card(
            "🟠", str(summary['unmatched_backend_count']), "UNMATCHED BACKEND", "No payment found",
            None, None, top_border_color="#f97316"
        ), unsafe_allow_html=True)
    with col7:
        st.markdown(render_kpi_card(
            "🟡", str(summary['partial_count']), "PARTIAL/DISCREPANT", "Amount/date mismatch",
            None, None, top_border_color="#eab308"
        ), unsafe_allow_html=True)
    with col8:
        dup_count = summary['duplicate_bank_count'] + summary['duplicate_backend_count']
        st.markdown(render_kpi_card(
            "🔵", str(dup_count), "DUPLICATES", "Duplicate references",
            None, None, top_border_color="#3b82f6"
        ), unsafe_allow_html=True)


def render_charts(result):
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="section-header" style="margin-bottom: 0px; font-size: 15px;"><span style="color: #3b82f6;">📊</span> Reconciliation Status</div>', unsafe_allow_html=True)
        
        status_data = {
            "Matched": len(result.matched),
            "Unmatched Bank": len(result.unmatched_bank),
            "Unmatched Backend": len(result.unmatched_backend),
            "Partial": len(result.partial),
        }
        total_records = sum(status_data.values())
        
        status_df = pd.DataFrame({
            "Status": [f"{k} {int(v/total_records*100)}%" if total_records > 0 else k for k, v in status_data.items()], 
            "Count": list(status_data.values())
        })
        
        # Colors: Green, Red, Orange, Yellow
        colors = ["#10b981", "#ef4444", "#f97316", "#eab308"]
        
        fig = go.Figure(data=[go.Pie(
            labels=status_df["Status"],
            values=status_df["Count"],
            hole=0.7,
            marker=dict(colors=colors, line=dict(color='white', width=3)),
            textinfo='none',
            hovertemplate='<b>%{label}</b><br>Count: %{value}<extra></extra>'
        )])
        
        fig.update_layout(
            showlegend=True,
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.0, font=dict(size=12, color="#475569")),
            margin=dict(t=10, b=10, l=10, r=100),
            height=250,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            annotations=[dict(text=f"{total_records}<br><span style='font-size:12px;font-weight:normal'>Total</span>", x=0.5, y=0.5, font_size=24, font_color="#0f172a", font_weight="bold", showarrow=False)]
        )
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="section-header" style="margin-bottom: 0px; font-size: 15px;"><span style="color: #ef4444;">📈</span> Match Quality Breakdown</div>', unsafe_allow_html=True)
        
        if not result.matched.empty:
            reason_counts = result.matched["reason_code"].value_counts().reset_index()
            reason_counts.columns = ["Reason", "Count"]
            
            reason_labels = {
                "MATCHED_EXACT_REF": "Exact Reference",
                "MATCHED_AMOUNT_DATE": "Amount + Date",
                "MATCHED_FUZZY_REF": "Fuzzy Reference",
                "MATCHED_DATE_WINDOW": "Date Window",
                "MATCHED_OFFLINE_WINDOW": "Offline Window",
                "MATCHED_NAME_FUZZY": "Name Fuzzy"
            }
            reason_counts["Reason"] = reason_counts["Reason"].map(reason_labels).fillna(reason_counts["Reason"])
            # Reverse sort so largest is at the top in horizontal bar
            reason_counts = reason_counts.sort_values(by="Count", ascending=True)
            
            fig2 = go.Figure()
            
            # Map standard colors to reasons (Green, Blue, Purple, Orange)
            bar_colors = []
            for reason in reason_counts["Reason"]:
                if "Exact" in reason: bar_colors.append("#10b981")
                elif "Amount" in reason: bar_colors.append("#3b82f6")
                elif "Fuzzy" in reason: bar_colors.append("#8b5cf6")
                else: bar_colors.append("#f97316")
                
            fig2.add_trace(go.Bar(
                y=reason_counts["Reason"],
                x=reason_counts["Count"],
                orientation='h',
                marker=dict(
                    color=bar_colors,
                    line=dict(color='white', width=1),
                ),
                text=reason_counts["Count"],
                textposition='outside',
                textfont=dict(size=12, color='#0f172a', weight='bold'),
                hovertemplate='<b>%{y}</b><br>Matched: %{x}<extra></extra>'
            ))
            
            fig2.update_layout(
                margin=dict(t=10, b=10, l=10, r=40),
                height=250,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, tickfont=dict(size=12, color='#475569')),
                bargap=0.4,
                showlegend=False
            )
            
            st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
        else:
            st.markdown('<div class="empty-state" style="padding:30px;"><div class="empty-state-icon">📊</div><p>No matched records to display</p></div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)


def render_data_tabs(result):
    tabs = st.tabs([
        f"🟢 Matched ({len(result.matched)})",
        f"🔴 Unmatched Bank ({len(result.unmatched_bank)})",
        f"🟠 Unmatched Backend ({len(result.unmatched_backend)})",
        f"🟡 Partial ({len(result.partial)})",
        f"🔵 Duplicates ({len(result.duplicates_bank) + len(result.duplicates_backend)})",
    ])
    
    with tabs[0]:
        if result.matched.empty:
            st.markdown('<div class="empty-state"><div class="empty-state-icon">✅</div><p>No matched records found</p></div>', unsafe_allow_html=True)
        else:
            st.dataframe(result.matched, use_container_width=True, height=450)
    
    with tabs[1]:
        if result.unmatched_bank.empty:
            st.markdown('<div class="empty-state"><div class="empty-state-icon">🏦</div><p>All bank records are matched</p></div>', unsafe_allow_html=True)
        else:
            st.dataframe(result.unmatched_bank, use_container_width=True, height=450)
    
    with tabs[2]:
        if result.unmatched_backend.empty:
            st.markdown('<div class="empty-state"><div class="empty-state-icon">📋</div><p>All backend records are matched</p></div>', unsafe_allow_html=True)
        else:
            st.dataframe(result.unmatched_backend, use_container_width=True, height=450)
    
    with tabs[3]:
        if result.partial.empty:
            st.markdown('<div class="empty-state"><div class="empty-state-icon">⚠️</div><p>No partial or discrepant records</p></div>', unsafe_allow_html=True)
        else:
            st.dataframe(result.partial, use_container_width=True, height=450)
    
    with tabs[4]:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<p style="font-size: 14px; font-weight: 600; color: #0f172a; margin-bottom: 12px;">🏦 Duplicate Bank References</p>', unsafe_allow_html=True)
            if result.duplicates_bank.empty:
                st.markdown('<p style="color: #94a3b8; text-align: center; padding: 40px;">No duplicates found</p>', unsafe_allow_html=True)
            else:
                st.dataframe(result.duplicates_bank, use_container_width=True, height=300)
        with c2:
            st.markdown('<p style="font-size: 14px; font-weight: 600; color: #0f172a; margin-bottom: 12px;">📋 Duplicate Backend References</p>', unsafe_allow_html=True)
            if result.duplicates_backend.empty:
                st.markdown('<p style="color: #94a3b8; text-align: center; padding: 40px;">No duplicates found</p>', unsafe_allow_html=True)
            else:
                st.dataframe(result.duplicates_backend, use_container_width=True, height=300)


def main():
    if not run_clicked:
        st.markdown("""
        <div class="empty-state" style="padding: 100px 20px;">
            <div class="empty-state-icon">📁</div>
            <h3 style="color: #0f172a; margin-bottom: 8px;">Ready to Reconcile</h3>
            <p style="color: #64748b; max-width: 400px; margin: 0 auto; line-height: 1.6;">
                Upload your <b>Bank Statement</b> and <b>Backend Membership Data</b> in the sidebar, 
                then click <b>Run Reconciliation</b> to see the magic happen.
            </p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    if bank_file is None or backend_file is None:
        st.error("⚠️ Please upload both files before running reconciliation.")
        return
    
    with st.spinner("🔍 Analyzing and matching records..."):
        try:
            bank_df, backend_df, config = load_dataframes(
                bank_file.getvalue(),
                backend_file.getvalue(),
                bank_file.name,
                backend_file.name,
            )
        except Exception as e:
            st.error(f"❌ Error loading files: {e}")
            return
    
    st.success(f"✅ Successfully loaded **{len(bank_df)}** bank rows and **{len(backend_df)}** backend rows.")
    
    with st.spinner("⚡ Running intelligent matching engine..."):
        result = reconcile(bank_df, backend_df, config)
    
    report_path = ROOT / "frontend" / "tmp_uploads" / "reconciliation_report.xlsx"
    write_report(result, report_path)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Summary Dashboard
    render_kpis(result.summary)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Charts
    render_charts(result)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Download Section
    col_dl1, col_dl2, col_spacer, col_time = st.columns([1.5, 1.5, 4, 2])
    with col_dl1:
        with open(report_path, "rb") as f:
            st.download_button(
                label="📥 Download Excel Report",
                data=f,
                file_name="reconciliation_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
    with col_dl2:
        audit_path = report_path.with_suffix(".audit_log.json")
        if audit_path.exists():
            with open(audit_path, "rb") as f:
                st.download_button(
                    label="📄 Download Audit Log",
                    data=f,
                    file_name="reconciliation_report.audit_log.json",
                    mime="application/json",
                    use_container_width=True,
                )
    with col_time:
        st.markdown('<p style="text-align: right; color: #64748b; font-size: 13px; margin-top: 10px;">Last updated: Just now</p>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Detailed Results
    render_data_tabs(result)


if __name__ == "__main__":
    main()
