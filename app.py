"""
Main Streamlit Application
AI Smart Store Inventory & Billing System
"""
import streamlit as st
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from database.db_manager import DatabaseManager
from detection.object_detector import ObjectDetector
from billing.billing_system import BillingSystem
from utils.helpers import VoiceAnnouncer, PDFInvoiceGenerator, Logger

# Page configuration
st.set_page_config(
    page_title="AI Smart Store",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'db_manager' not in st.session_state:
    st.session_state.db_manager = DatabaseManager()

if 'billing_system' not in st.session_state:
    st.session_state.billing_system = BillingSystem(st.session_state.db_manager)

if 'voice_announcer' not in st.session_state:
    st.session_state.voice_announcer = VoiceAnnouncer()

if 'pdf_generator' not in st.session_state:
    st.session_state.pdf_generator = PDFInvoiceGenerator()

if 'logger' not in st.session_state:
    st.session_state.logger = Logger()

# Custom CSS
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        margin: 5px;
    }
    h1 {
        color: #0066cc;
        text-align: center;
    }
    .success-box {
        background-color: #d4edda;
        color: #155724;
        padding: 15px;
        border-radius: 5px;
        border-left: 4px solid #28a745;
    }
    .warning-box {
        background-color: #fff3cd;
        color: #856404;
        padding: 15px;
        border-radius: 5px;
        border-left: 4px solid #ffc107;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("🏪 Smart Store System")
page = st.sidebar.radio(
    "Navigate to:",
    ["Dashboard", "Live Camera Scanner", "Product Management", 
     "Inventory Management", "Billing History", "Settings"]
)

# Main content
if page == "Dashboard":
    from pages import dashboard
    dashboard.show()
elif page == "Live Camera Scanner":
    from pages import camera_scanner
    camera_scanner.show()
elif page == "Product Management":
    from pages import product_management
    product_management.show()
elif page == "Inventory Management":
    from pages import inventory_management
    inventory_management.show()
elif page == "Billing History":
    from pages import billing_history
    billing_history.show()
elif page == "Settings":
    from pages import settings
    settings.show()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #888; font-size: 12px;'>
        <p>AI Smart Store Inventory & Billing System v1.0</p>
        <p>Powered by YOLO Object Detection | Built with Streamlit</p>
    </div>
    """,
    unsafe_allow_html=True
)
