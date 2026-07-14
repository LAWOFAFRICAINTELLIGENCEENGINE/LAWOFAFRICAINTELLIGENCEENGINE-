import streamlit as st
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities.hasher import Hasher
from sqlalchemy import text
from groq import Groq
import pandas as pd
import json
import PyPDF2  

# ==========================================
# 1. CORE INFRASTRUCTURE & CSS
# ==========================================
st.set_page_config(page_title="Law of Africa Engine", page_icon="⚖️", layout="wide")

st.markdown("""
<style>
[data-testid="stChatInputSubmitButton"] {
    background-color: #D4AF37 !important; 
    color: black !important;
    border-radius: 50% !important;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATABASE & STATE INITIALIZATION
# ==========================================
try:
    conn = st.connection("postgresql", type="sql")
except Exception as e:
    st.warning("Database connection initializing. Ensure st.secrets are configured.")

if "messages" not in st.session_state:
    st.session_state.messages = []
    
if "pdf_knowledge_base" not in st.session_state:
    st.session_state.pdf_knowledge_base = ""

# ==========================================
# 3. AUTHENTICATION GATEWAY
# ==========================================
try:
    authenticator = stauth.Authenticate(
        st.secrets["credentials"],
        st.secrets["cookie"]["name"],
        st.secrets["cookie"]["key"],
        st.secrets["cookie"]["expiry_days"]
    )
    
    authenticator.login(location="main")
except Exception as e:
    st.error("Authentication module awaiting configuration in st.secrets.")
    st.stop()

# ==========================================
# 4. REGISTRATION LOGIC 
# ==========================================
if st.session_state.get("authentication_status") is False:
    st.error("❌ Incorrect username or password!")
    
elif st.session_state.get("authentication_status") is None:
    tab1, tab2 = st.tabs(["Login", "Register New User"])
    
    with tab2:
        st.subheader("Register a New Account")
        new_user = st.text_input("Username")
        new_name = st.text_input("Full Name")
        new_pass = st.text_input("Password", type="password")
        
        if st.button("Create Account"):
            hashed_pass = Hasher([new_pass]).generate()[0] 
            try:
                with conn.session as s:
                    s.execute(
                        text("INSERT INTO users (username, name, password, query_count) VALUES (:u, :n, :p, 0)"), 
                        {"u": new_user, "n": new_name, "p": hashed_pass}
                    )
                    s.commit()
                st.success("Account created successfully! Switch to the Login tab.")
            except Exception as e:
                st.error(f"Database deployment failure: {e}")

# ==========================================
# 5. ENTERPRISE ARCHITECTURE
# ==========================================
elif st.session_state.get("authentication_status"):
    current_username = st.session_state["username"]
    
    # --- FETCH USER BANDWIDTH ON LOAD ---
    try:
        with conn.session as s:
            result = s.execute(text("SELECT query_count FROM users WHERE username = :u"), {"u": current_username}).fetchone()
            user_queries = result[0] if result else 0
    except:
        user_queries = 0

    # --- MULTI-NODE ROUTING PROTOCOL ---
    with st.sidebar:
        st.title("🎛️ Legal Routing")
        st.write(f"Active Operator: **{current_username}**")
        st.write(f"📊 **Bandwidth Used:** {user_queries} / 3 Queries")
        authenticator.logout("Terminate Secure Session", "sidebar")
        
        st.divider()
        active_node = st.radio("Active Node", ["Citizen Access Node 🌍", "Corporate Counsel Node 💼", "Chief Justice Telemetry 📊"])
        
        if st.button("🗑️ Clear Active Memory"):
            st.session_state.messages = []
            st.rerun()

    legal_database = {
        "Constitution of Nigeria (Sec 33)": {"Category": "Human Rights", "Jurisdiction": "Nigeria", "Statute": "Right to life. No person shall be deprived intentionally of his life..."},
        "AfCFTA Article 3": {"Category": "Trade Law", "Jurisdiction": "Pan-African", "Statute": "Create a single continental market for goods and services..."}
    }
    legal_json = json.dumps(legal_database, indent=2)

    # ==========================================
    # 6. BIG DATA INGESTION (Chief Justice View)
    # ==========================================
    if active_node == "Chief Justice Telemetry 📊":
        st.title("📊 Chief Justice Telemetry")
        st.write("Secure infrastructure metrics and document ingestion.")
        
        st.subheader("📥 Dynamic Legal Ingestion Engine")
        uploaded_file = st.file_uploader("Upload PDF Document", type=["pdf"])
        
        if uploaded_file is not None:
            try:
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                extracted_text = ""
                for page in pdf_reader.pages:
                    extracted_text += page.extract_text() + "\n"
                
                st.session_state.pdf_knowledge_base = extracted_text
                st.success(f"✅ Neural Ingestion Complete: {len(pdf_reader.pages)} pages dynamically memorized.")
            except Exception as e:
                st.error(f"Failed to process document: {e}")
                
        if st.session_state.pdf_knowledge_base:
            st.info("🧠 Engine Memory Status: ACTIVE (PDF Data Loaded)")

        st.divider()
        col1, col2, col3 = st.columns(3)
        col1.metric(label=f"Queries Processed ({current_username})", value=user_queries)
        col2.metric(label="System Status", value="Encrypted")
        col3.metric(label="Inference Latency", value="<15ms")

    # ==========================================
    # 7. AUTONOMOUS LEGAL INFERENCE INTERFACE
    # ==========================================
    else: 
        st.title(f"⚖️ {active_node}")
        
        try:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        except Exception:
            st.error("Authentication Error: Missing API Credentials.")
            st.stop()

        dynamic_memory = st.session_state.pdf_knowledge_base

        if active_node == "Citizen Access Node 🌍":
            system_directive = f"""You are the Law of Africa Citizen Node. Explain legal statutes simply. 
            BASE KNOWLEDGE: {legal_json}
            DYNAMIC UPLOADED MEMORY (PDF TEXT): {dynamic_memory}"""
        else:
            system_directive = f"""You are the Law of Africa Corporate Counsel Node. Provide high-level technical legal analysis.
            BASE KNOWLEDGE: {legal_json}
            DYNAMIC UPLOADED MEMORY (PDF TEXT): {dynamic_memory}"""
            
        system_prompt = {"role": "system", "content": system_directive}

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        # ==========================================
        # 💰 PHASE 3: THE REVENUE PAYWALL LOGIC
        # ==========================================
        if user_queries >= 3:
            st.error("🔒 **FREE TIER EXHAUSTED**")
            st.warning("You have reached your limit of 3 free legal queries. The computational engine is currently locked.")
            st.write("Upgrade to **Law of Africa Premium** to unlock unlimited queries, deeper PDF ingestion, and corporate legal analysis.")
            
            # --- REAL PAYMENT GATEWAY LINK ---
            # Create a real payment link on Paystack or Stripe and paste the URL here:
            PAYMENT_URL = "https://paystack.com/pay/law-of-africa-premium" 
            
            st.link_button("💳 Upgrade to Premium Now", PAYMENT_URL, type="primary")
            
        else:
            # If they have less than 3 queries, show the chat box
            prompt = st.chat_input(f"Enter legal query... ({3 - user_queries} free queries remaining)")

            if prompt:
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.write(prompt)
                
                with st.chat_message("assistant"):
                    conversation_history = [system_prompt] + st.session_state.messages
                    
                    try:
                        response = client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=conversation_history,
                            temperature=0.1 
                        )
                        engine_response = response.choices[0].message.content
                        st.write(engine_response)
                    except Exception as e:
                        engine_response = f"Cloud Execution Failure: {e}"
                        st.error(engine_response)
                    
                st.session_state.messages.append({"role": "assistant", "content": engine_response})
                
                # --- UPDATE DATABASE BANDWIDTH ---
                try:
                    with conn.session as s:
                        s.execute(text("UPDATE users SET query_count = query_count + 1 WHERE username = :u"), {"u": current_username})
                        s.commit()
                except Exception as e:
                    st.error(f"Failed to update query telemetry: {e}")
                    
                st.rerun()
