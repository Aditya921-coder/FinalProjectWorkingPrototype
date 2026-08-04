#Initialize the file with the command: 'streamlit run app.py' in one terminal instance

import io
import requests
import networkx as nx
import matplotlib.pyplot as plt
import streamlit as st
from fpdf import FPDF

# Set Page Config
st.set_page_config(
    page_title="MHA Cyber Crime Investigation Suite", 
    page_icon="🛡️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Enterprise CSS Styling
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1f2937; padding: 15px; border-radius: 10px; border: 1px solid #374151; }
    .status-badge { background-color: #059669; color: white; padding: 4px 12px; border-radius: 20px; font-weight: bold; font-size: 12px; }
    div[data-testid="stForm"] { border: 1px solid #374151; border-radius: 10px; padding: 20px; }
    </style>
""", unsafe_allow_html=True)

API_URL = "http://127.0.0.1:8000"

# Sidebar Branding & Navigation
st.sidebar.markdown("## 🛡️ **MHA Cyber Crime**")
st.sidebar.title("MHA Cyber Crime Portal")
st.sidebar.caption("Ministry of Home Affairs | Govt. of India")
st.sidebar.markdown("---")

page = st.sidebar.radio("Navigation Module", [
    "1. Case Creation & OCR", 
    "2. Mind Map & Investigation Hub", 
    "3. Summarization & PDF Reporting"
])

st.sidebar.markdown("---")
st.sidebar.subheader("System Health")
st.sidebar.markdown("**Backend API:** Online (`localhost:8000`)")
st.sidebar.markdown("**SQLite DB:** Active")
st.sidebar.markdown("**AI Processing:** Local Tesseract Ready")

# Global Header KPI Metrics
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric("Active Investigations", "14", "+2 Today")
col_m2.metric("Total Fraud Amount", "Rs. 12,45,000", "High Alert")
col_m3.metric("Action Requests Sent", "38", "8 Pending")
col_m4.metric("Avg Resolution Time", "4.2 Days", "-12% improvement")

st.markdown("---")

# -------------------------------------------------------------
# PHASE 1: CASE CREATION
# -------------------------------------------------------------
if page == "1. Case Creation & OCR":
    st.header("Phase 1: Case Ingestion & Intelligent Parsing")
    st.caption("Upload NCP complaints or manually populate case file details below.")

    col_left, col_right = st.columns([1, 2])

    with col_left:
        st.subheader("1. Ingest Document")
        uploaded_file = st.file_uploader("Upload NCP Receipt / FIR (PDF/PNG)", type=["pdf", "png", "jpg"])
        
        run_ocr = st.button("Run OCR Extraction", use_container_width=True)
        demo_load = st.button("Quick-Load Sample Demo Data", use_container_width=True)

        if run_ocr:
            if uploaded_file is not None:
                with st.spinner("Executing Local OCR Processing..."):
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    try:
                        res = requests.post(f"{API_URL}/upload_ncp_pdf", files=files).json()
                        if res.get("status") == "success":
                            st.session_state["ocr_data"] = res["extracted"]
                            st.success("OCR Processing Complete!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Backend server offline or unreachable! Error: {e}")
            else:
                st.warning("Please upload a file first before running OCR.")

        if demo_load:
            st.session_state["ocr_data"] = {
                "case_id": "CC/2026/0701/000123",
                "ack_no": "NCP/2026/0701/000123",
                "fir_no": "FIR/2026/0701",
                "victim_name": "Anurag Sharma",
                "victim_phone": "+91 98765 43210",
                "suspect_phone": "+91 91234 56789",
                "disputed_amount": 50000.00,
                "priority": "High",
                "data_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
            }
            st.success("Sample Demo Data Loaded!")
            st.rerun()

    with col_right:
        st.subheader("2. Extracted Case Details & Officer Assignment")
        
        data = st.session_state.get("ocr_data", {})

        with st.form("case_form"):
            c1, c2 = st.columns(2)
            with c1:
                case_id = st.text_input("Case ID", value=data.get("case_id", "CC/2026/0701/000123"))
                ack_no = st.text_input("Acknowledgment No.", value=data.get("ack_no", ""))
                fir_no = st.text_input("FIR No.", value=data.get("fir_no", ""))
                victim_name = st.text_input("Victim Name", value=data.get("victim_name", "Harsh Singh"))
                victim_phone = st.text_input("Victim Phone", value=data.get("victim_phone", ""))
            
            with c2:
                suspect_phone = st.text_input("Suspect Phone", value=data.get("suspect_phone", ""))
                try:
                    amt_val = float(data.get("disputed_amount", 0.0))
                except (ValueError, TypeError):
                    amt_val = 0.0

                disputed_amount = st.number_input("Disputed Amount (Rs.)", value=amt_val, step=500.0)
                
                p_idx = 0 if data.get("priority", "High") == "High" else 1
                priority = st.selectbox("Case Priority", ["High", "Medium", "Low"], index=p_idx)
                assigned_io = st.selectbox("Assign IO Officer", ["Inspector Rajesh Kumar", "Sub-Inspector Amit Varma", "IO Priya Singh"])
                data_hash = st.text_input("Cryptographic SHA-256 Hash", value=data.get("data_hash", ""))

            submit = st.form_submit_button("Save Case & Dispatch to IO Workflow", use_container_width=True)
            
            if submit:
                payload = {
                    "case_id": str(case_id), 
                    "ack_no": str(ack_no), 
                    "fir_no": str(fir_no),
                    "victim_name": str(victim_name), 
                    "victim_phone": str(victim_phone),
                    "suspect_phone": str(suspect_phone), 
                    "disputed_amount": str(disputed_amount),
                    "priority": str(priority), 
                    "data_hash": str(data_hash)
                }
    
                try:
                    res = requests.post(f"{API_URL}/save_case", data=payload)
                    if res.status_code == 200:
                        save_res = res.json()
                        st.success(f"{save_res.get('status', 'Success')} | Assigned to {assigned_io}")
                    else:
                        st.error(f"Backend returned status {res.status_code}: {res.text}")
                except Exception as e:
                    st.error(f"Could not reach backend server: {e}")

# -------------------------------------------------------------
# PHASE 2: IO MIND MAP & LOGGING
# -------------------------------------------------------------
elif page == "2. Mind Map & Investigation Hub":
    st.header("Phase 2: Investigator Control Room & Money Trail Mind Map")
    
    col_input, col_status = st.columns([3, 1])
    with col_input:
        case_id_input = st.text_input("Active Case ID:", "CC/2026/0701/000123")
    with col_status:
        st.markdown("<br>", unsafe_allow_html=True)
        load_btn = st.button("Load Investigation Workspace", use_container_width=True)

    if load_btn or st.session_state.get("loaded_case"):
        st.session_state["loaded_case"] = True
        try:
            res = requests.get(f"{API_URL}/get_case/{case_id_input}").json()
            if "error" in res:
                st.error("Case Not Found! Create it in Phase 1 first or click 'Quick-Load' in Phase 1.")
            else:
                st.markdown(f"### Case Overview: `{res['case_id']}` | Status: <span class='status-badge'>UNDER INVESTIGATION</span>", unsafe_allow_html=True)
                
                tab1, tab2, tab3 = st.tabs(["Fund Flow Graph", "Action Request Dispatcher", "Case Diaries"])
                
                with tab1:
                    st.write("#### AI Generated Fund Flow Mind Map")
                    G = nx.DiGraph()
                    for tx in res["transactions"]:
                        G.add_edge(tx["sender"], tx["receiver"], label=f"Rs. {tx['amount']:,.0f}")
                    
                    pos = nx.spring_layout(G, seed=42)
                    
                    fig, ax = plt.subplots(figsize=(11, 4.5))
                    fig.patch.set_facecolor('#0e1117')
                    ax.set_facecolor('#0e1117')
                    
                    nx.draw_networkx_nodes(
                        G, pos, 
                        node_shape='s', 
                        node_size=6000, 
                        node_color='#1e293b', 
                        edgecolors='#3b82f6', 
                        linewidths=2, 
                        ax=ax
                    )
                    
                    nx.draw_networkx_edges(
                        G, pos, 
                        edge_color='#94a3b8', 
                        arrowsize=20, 
                        arrowstyle='->', 
                        width=2, 
                        connectionstyle="arc3,rad=0.1", 
                        ax=ax
                    )
                    
                    formatted_labels = {node: node.replace(" ", "\n", 2) for node in G.nodes()}
                    nx.draw_networkx_labels(
                        G, pos, 
                        labels=formatted_labels, 
                        font_size=8, 
                        font_color='#f8fafc', 
                        font_weight='bold', 
                        ax=ax
                    )
                    
                    edge_labels = nx.get_edge_attributes(G, 'label')
                    nx.draw_networkx_edge_labels(
                        G, pos, 
                        edge_labels=edge_labels, 
                        font_color='#fbbf24', 
                        font_size=9, 
                        font_weight='bold', 
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='#0e1117', edgecolor='#fbbf24', alpha=0.9), 
                        ax=ax
                    )
                    
                    plt.margins(0.25)
                    plt.axis('off')
                    st.pyplot(fig)

                with tab2:
                    st.write("#### Dispatch Formal Nodal Requests")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.selectbox("Request Type", ["CDR (Call Detail Records)", "IPDR (IP Detail Records)", "CAF / Subscriber KYC", "Bank Freeze Order"])
                        st.text_input("Target Authority / Bank", "Airtel Telecommunications / ICICI Bank")
                    with col2:
                        st.text_area("Legal Justification / Remarks", "Urgent request in connection with fraudulent money trail under Sec 91 CrPC.")
                        if st.button("Issue Official Request"):
                            st.success("Request generated and logged to audit trail!")

                with tab3:
                    st.write("#### Case Diary Entries (Voice / Text)")
                    st.text_area("New Diary Entry (Hindi / English)", "Suspect identified near ATM location in Rohini, Delhi. Requesting CCTV footage.")
                    st.button("Save Diary Entry")

        except Exception as e:
            st.error(f"Backend offline or execution error: {e}")

# -------------------------------------------------------------
# PHASE 3: SUMMARIZATION & PDF REPORT
# -------------------------------------------------------------
elif page == "3. Summarization & PDF Reporting":
    st.header("Phase 3: Automated Case Timeline & Court PDF Export")
    
    case_id_input = st.text_input("Target Case ID:", "CC/2026/0701/000123")
    
    if st.button("Generate Comprehensive Report", use_container_width=True):
        try:
            res = requests.get(f"{API_URL}/get_case/{case_id_input}").json()
            if "error" not in res:
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Chronological Incident Timeline")
                    st.info("**01/07/2026 09:45 AM**: Complaint Registered on NCP Portal")
                    st.info(f"**01/07/2026 10:15 AM**: Rs. {res['disputed_amount']:,.2f} Transferred to Layer 1 Account")
                    st.info("**02/07/2026 12:00 PM**: CDR & CAF Requests Sent to Telecom")
                    st.info("**07/07/2026 03:00 PM**: Primary Suspect Identified")
                
                with col2:
                    st.subheader("AI Executive Summary")
                    summary_text = (
                        f"Victim {res['victim_name']} was defrauded of Rs. {res['disputed_amount']:,.2f}.\n"
                        f"Money trail analysis reveals funds moved from Victim -> Layer 1 Fraudulent Account -> Layer 2 Account & ATM Cash Withdrawal in Delhi.\n"
                        f"Primary accused identified via CAF/CDR analysis."
                    )
                    st.text_area("Summary Preview", summary_text, height=180)
                    
                    # Clean PDF creation in memory
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", size=12)
                    pdf.cell(190, 10, txt="GOVERNMENT OF INDIA - CYBER CRIME REPORT", ln=1, align="C")
                    pdf.cell(190, 10, txt=f"Case ID: {res['case_id']}", ln=2)
                    pdf.cell(190, 10, txt=f"Victim: {res['victim_name']} | FIR: {res['fir_no']}", ln=3)
                    pdf.cell(190, 10, txt=f"Disputed Amount: Rs. {res['disputed_amount']:,.2f}", ln=4)
                    pdf.ln(5)
                    pdf.multi_cell(0, 10, txt=summary_text)
                    
                    pdf_bytes = pdf.output(dest='S').encode('latin-1')
                    
                    st.download_button(
                        label="⬇ Download Official PDF Report",
                        data=pdf_bytes,
                        file_name=f"Report_{res['case_id'].replace('/', '_')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
            else:
                st.error("Case not found in database! Save the case in Phase 1 first.")
        except Exception as e:
            st.error(f"Error generating report: {e}")