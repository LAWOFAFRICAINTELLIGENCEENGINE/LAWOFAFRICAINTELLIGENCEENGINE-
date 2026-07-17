import streamlit as st
import streamlit_authenticator as stauth
import PyPDF2
from openai import OpenAI
from sqlalchemy import text
import json

# 

# 1. SYSTEM CONFIGURATION & SECURITY
# 


st.set_page_config(
    page_title="Law of Africa Intelligence Engine", 
    page_icon="⚖️", 
    layout="wide"
)

# --- CUSTOM APP STYLING ---
st.markdown("""
<style>
    /* Hide Streamlit's default top menu and footer for a clean mobile look */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Make the main background flush with the screen */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 5rem;
    }

    /* Style the chat bubbles to look modern and rounded */
    .stChatMessage {
        background-color: #1E1E1E; 
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 10px;
        border: 1px solid #333333;
    }
    
    /* Smooth out the bottom chat input box */
    .stChatInput {
        border-radius: 25px !important;
        background-color: #1E1E1E !important;
    }
</style>
""", unsafe_allow_html=True)

# Safely initialize Database Connection
try:
    conn = st.connection("postgresql", type="sql")
except Exception:
    conn = None

# Base Knowledge Placeholder
try:
    with open("legal_knowledge.json", "r") as file:
        legal_json = json.load(file)
except Exception:
    legal_json = "Base legal knowledge pending upload."

# 

# 2. AUTHENTICATION LOGIC (The Vault)
# 


try:
    # Converting read-only secrets into an editable photocopy 
    credentials = st.secrets["credentials"].to_dict()
    cookie = st.secrets["cookie"].to_dict()
    
    authenticator = stauth.Authenticate(
        credentials,
        cookie["name"],
        cookie["key"],
        cookie["expiry_days"],
        st.secrets.get("preauthorized", {"emails": []})
    )
    
    authenticator.login(location="main")

except Exception as e:
    st.error("🚨 SECRETS DIAGNOSTIC MODE ACTIVE 🚨")
    st.error(f"The exact missing piece is: **{e}**")
    st.stop()

# 

# 3. REGISTRATION LOGIC
# 


if st.session_state.get("authentication_status") is False:
    st.error("❌ Incorrect username or password!")

elif st.session_state.get("authentication_status") is None:
    tab1, tab2 = st.tabs(["Login", "Register New User"])

    with tab2:
        st.subheader("Register a New Account")
        new_user = st.text_input("Username")
        new_name = st.text_input("Full Name")
        new_pass = st.text_input("Password", type="password")
        # if st.button("Create Account"): 
        # (Your database account creation logic goes here)

# 

# 4. MAIN APP ROUTING & UI
# 


if st.session_state.get("authentication_status"):
    current_username = st.session_state["username"]
    
    # Sidebar Navigation & AI Engine Selector
    with st.sidebar:
        st.write(f"Welcome, **{st.session_state['name']}**")
        
        st.divider()
        st.write("⚙️ **Engine Settings**")
        # CHANGED: Now a line-by-line list instead of a dropdown box!
        ai_engine = st.radio("🧠 Select AI Engine", ["Groq (Llama-3)", "Gemini (Google)", "Grok (Elon AI)"])
        
        st.divider()
        authenticator.logout("Logout", "sidebar")


    # 

    # 5. BIG DATA INGESTION (Chief Justice View)
    # 

    
    # CHANGED: Removed the Dashboard menu. It goes straight to the chat now!
    st.title("🏛️ Law of Africa Intelligence Engine")
    st.write(f"Secure infrastructure metrics. Currently routed through: **{ai_engine}**")

    # --- SECURE PDF UPLOADER ---
    st.subheader("📥 Dynamic Legal Ingestion Engine")
    
    uploaded_file = st.file_uploader("Upload PDF Document", type=["pdf"])

    if uploaded_file is not None:
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            extracted_text = ""
            for page in pdf_reader.pages:
                extracted_text += page.extract_text() + "\n"
            
            dynamic_memory = extracted_text

            system_directive = f"""
            BASE KNOWLEDGE: {legal_json}
            DYNAMIC UPLOADED MEMORY (PDF TEXT): {dynamic_memory}
            If the user asks about the uploaded document, use the DYNAMIC UPLOADED MEMORY to analyze it."""

            system_prompt = {"role": "system", "content": system_directive}

            if "messages" not in st.session_state:
                st.session_state.messages = []

            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.write(message["content"])

            prompt = st.chat_input("Enter legal query or statute parameter...")

            if prompt:
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.write(prompt)

                with st.chat_message("assistant"):
                    conversation_history = [system_prompt] + st.session_state.messages

                    # --- MULTI-MODEL ROUTING LOGIC ---
                    try:
                        # 1. Determine which keys and URLs to use based on the list
                        if ai_engine == "Groq (Llama-3)":
                            api_key = st.secrets.get("GROQ_API_KEY")
                            base_url = "https://api.groq.com/openai/v1"
                            model_name = "llama-3.1-8b-instant"
                        elif ai_engine == "Gemini (Google)":
                            api_key = st.secrets.get("GEMINI_API_KEY")
                            base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
                            model_name = "gemini-1.5-flash"
                        elif ai_engine == "Grok (Elon AI)":
                            api_key = st.secrets.get("GROK_API_KEY")
                            base_url = "https://api.x.ai/v1"
                            model_name = "grok-beta"

                        # 2. Check if the key exists
                        if not api_key:
                            st.error(f"⚠️ {ai_engine} API Key missing in st.secrets!")
                            st.stop()

                        # 3. Spin up the specific AI engine requested
                        active_client = OpenAI(api_key=api_key, base_url=base_url)
                        
                        # 4. Generate the response
                        response = active_client.chat.completions.create(
                            model=model_name,
                            messages=conversation_history,
                            temperature=0.1
                        )
                        engine_response = response.choices[0].message.content
                        st.write(engine_response)
                        
                    except Exception as e:
                        engine_response = f"Cloud Execution Failure ({ai_engine}): {e}"
                        st.error(engine_response)

                st.session_state.messages.append({"role": "assistant", "content": engine_response})

                # --- BANDWIDTH TRACKING ---
                if conn:
                    try:
                        with conn.session as s:
                            s.execute(text("UPDATE users SET query_count = query_count + 1 WHERE username = :u"), {"u": current_username})
                            s.commit()
                    except Exception as e:
                        pass

                st.rerun()

        except Exception as e:
            st.error(f"Failed to process PDF: {e}") 
