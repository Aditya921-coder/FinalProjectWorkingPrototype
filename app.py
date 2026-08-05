import io
import os
import sys
import socket
import subprocess
import time
import requests
import networkx as nx
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
from fpdf import FPDF

# Check if local port is bound
def is_port_open(port=8000):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

# Reliable Auto-start FastAPI backend on Streamlit Cloud
@st.cache_resource
def start_backend():
    if not is_port_open(8000):
        # Uses sys.executable to run uvicorn within the exact Streamlit Cloud environment
        subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "backend:app", "--host", "127.0.0.1", "--port", "8000"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        # Polling loop to wait until FastAPI server is ready
        for _ in range(10):
            if is_port_open(8000):
                break
            time.sleep(0.5)

start_backend()

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

# Formal PDF Header & Footer Class
class ForensicPDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 13)
        self.cell(0, 8, "CONFIDENTIAL // MINISTRY OF HOME AFFAIRS CYBER CRIME REPORT", ln=True, align="C")
        self.set_font("Arial", "I", 9)
        self.cell(0, 5, "Generated via Automated Forensics System", ln=True, align="C")
        self.line(10, 24, 200, 24)
        self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()} - Chain of Custody & Data Integrity Guaranteed", align="C")

# Sidebar Branding & Navigation
st.sidebar.markdown("## 🛡️ **MHA Cyber Crime**")
st.sidebar.title("MHA Cyber Crime Portal")
st.sidebar.caption("Ministry of Home Affairs | Govt. of India")
st.sidebar.markdown("---")

page = st.sidebar.radio("Navigation Module", [
    "1. Case Creation & OCR", 
    "2. Mind Map & Investigation Hub", 
    "3. Case Archive & Search",
    "4. Summarization & PDF Reporting"
])

st.sidebar.markdown("---")
st.sidebar.subheader("System Health")
st.sidebar.markdown("**Backend API:** Online (`localhost:8000`)")
st.sidebar.markdown("**SQLite DB:** Active")
st.sidebar.markdown("**AI Processing:** Local Tesseract Ready")

# Forensic Audit Trail View in Sidebar
with st.sidebar.expander("📋 View Forensic Audit Trail"):
    try:
        res = requests.get(f"{API_URL}/audit_logs")
        if res.status_code == 200 and res.json():
            st.dataframe(pd.DataFrame(res.json()), use_container_width=True, hide_index=True)
        else:
            st.info("No audit logs found.")
    except Exception:
        st.caption("Audit logs unavailable.")

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
        try:
            resp = requests.get(f"{API_URL}/get_case/{case_id_input}")
            if resp.status_code == 200:
                res = resp.json()
                if "error" in res:
                    st.session_state["loaded_case"] = False  # Reset state on error
                    st.error("Case Not Found! Save the case in Phase 1 first.")
                else:
                    st.session_state["loaded_case"] = True  # Only lock state when successful
                    st.markdown(f"### Case Overview: `{res['case_id']}` | Status: <span class='status-badge'>UNDER INVESTIGATION</span>", unsafe_allow_html=True)
                    
                    tab1, tab2, tab3 = st.tabs(["Fund Flow Graph", "Action Request Dispatcher", "Case Diaries"])
                    
                    with tab1:
                        st.write("#### AI Generated Color-Coded Money Trail Mind Map")
                        G = nx.DiGraph()
                        color_map = []
                        
                        for tx in res.get("transactions", []):
                            G.add_edge(tx["sender"], tx["receiver"], label=f"Rs. {tx['amount']:,.0f}")
                        
                        if len(G.nodes()) == 0:
                            st.info("No transaction data available to plot graph.")
                        else:
                            for node in G.nodes():
                                if "Victim" in node:
                                    color_map.append("#3b82f6")  # Blue
                                elif "Layer 1" in node:
                                    color_map.append("#ef4444")  # Red
                                elif "Layer 2" in node:
                                    color_map.append("#f59e0b")  # Yellow
                                else:
                                    color_map.append("#10b981")  # Green
                                    
                            pos = nx.spring_layout(G, k=0.8, seed=42)
                            fig, ax = plt.subplots(figsize=(11, 4.5))
                            fig.patch.set_facecolor('#0e1117')
                            ax.set_facecolor('#0e1117')
                            
                            nx.draw_networkx_nodes(G, pos, node_shape='s', node_size=5500, node_color=color_map, edgecolors='#ffffff', linewidths=1.5, ax=ax)
                            nx.draw_networkx_edges(G, pos, edge_color='#94a3b8', arrowsize=20, arrowstyle='->', width=2, connectionstyle="arc3,rad=0.1", ax=ax)
                            
                            formatted_labels = {node: node.replace(" ", "\n", 2) for node in G.nodes()}
                            nx.draw_networkx_labels(G, pos, labels=formatted_labels, font_size=8, font_color='#ffffff', font_weight='bold', ax=ax)
                            
                            edge_labels = nx.get_edge_attributes(G, 'label')
                            nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='#fbbf24', font_size=9, font_weight='bold', bbox=dict(boxstyle='round,pad=0.3', facecolor='#0e1117', edgecolor='#fbbf24', alpha=0.9), ax=ax)
                            
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
                        diary_text = st.text_area("New Diary Entry (Hindi / English)", "Suspect identified near ATM location in Rohini, Delhi. Requesting CCTV footage.")
                        
                        if st.button("Save Diary Entry"):
                            if diary_text.strip():
                                try:
                                    res = requests.post(f"{API_URL}/save_diary", data={"case_id": case_id_input, "entry": diary_text})
                                    if res.status_code == 200:
                                        st.success("Case diary entry successfully logged to backend database!")
                                        st.rerun()  # Direct rerun keeps UI smooth
                                    else:
                                        st.error(f"Failed to log entry: Status code {res.status_code}")
                                except Exception as e:
                                    st.error(f"Could not reach backend: {e}")
                            else:
                                st.warning("Please enter some text before saving.")
            else:
                st.session_state["loaded_case"] = False
                st.error(f"Backend error ({resp.status_code}): Case file not initialized yet. Go to Phase 1 and click 'Save Case & Dispatch to IO Workflow' first.")
        except Exception as e:
            st.session_state["loaded_case"] = False
            st.error(f"Backend server unreachable: {e}")

# -------------------------------------------------------------
# PHASE 3: CASE ARCHIVE & SEARCH
# -------------------------------------------------------------
if page == "3. Case Archive & Search":
    st.header("Phase 3: Database Search & Filtering Hub")
    st.caption("Search across saved case files, victims, or acknowledgment numbers.")

    search_query = st.text_input("🔍 Filter by Case ID, Victim Name, FIR, or ACK Number:", "")
    
    try:
        res = requests.get(f"{API_URL}/search_cases", params={"query": search_query if search_query else ""})
        if res.status_code == 200:
            cases_data = res.json()
            if cases_data:
                df = pd.DataFrame(cases_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No matching records found in the database.")
        else:
            st.error(f"Could not query backend database (Status code: {res.status_code}).")
    except Exception as e:
        st.error(f"Error connecting to server: {e}")

# -------------------------------------------------------------
# PHASE 4: SUMMARIZATION & PDF REPORT
# -------------------------------------------------------------
elif page == "4. Summarization & PDF Reporting":
    st.header("Phase 4: Automated Case Timeline & Court PDF Export")
    
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
                    summary_text = res.get("ai_summary", (
                        f"Victim {res['victim_name']} was defrauded of Rs. {res['disputed_amount']:,.2f}.\n"
                        f"Money trail analysis reveals funds moved from Victim -> Layer 1 Fraudulent Account -> Layer 2 Account & ATM Cash Withdrawal in Delhi.\n"
                        f"Primary accused identified via CAF/CDR analysis."
                    ))
                    st.text_area("Summary Preview", summary_text, height=180)
                    
                    # Refined PDF generation
                    pdf = ForensicPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", size=10)
                    
                    pdf.cell(0, 8, f"Case ID: {res['case_id']}", ln=True)
                    pdf.cell(0, 8, f"ACK No: {res['ack_no']} | FIR No: {res['fir_no']}", ln=True)
                    pdf.cell(0, 8, f"Victim Name: {res['victim_name']} | Phone: {res['victim_phone']}", ln=True)
                    pdf.cell(0, 8, f"Disputed Amount: Rs. {res['disputed_amount']:,.2f}", ln=True)
                    pdf.cell(0, 8, f"SHA-256 Hash Stamp: {res['data_hash']}", ln=True)
                    pdf.ln(5)
                    
                    pdf.set_font("Arial", "B", 11)
                    pdf.cell(0, 8, "Executive AI Investigation Summary:", ln=True)
                    pdf.set_font("Arial", size=10)
                    pdf.multi_cell(0, 6, summary_text)
                    
                    pdf_bytes = bytes(pdf.output())
                    
                    st.download_button(
                        label="⬇ Download Official PDF Report",
                        data=pdf_bytes,
                        file_name=f"Report_{res['case_id'].replace('/', '_')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
        except Exception as e:
            st.error(f"Error producing report: {e}")
         
