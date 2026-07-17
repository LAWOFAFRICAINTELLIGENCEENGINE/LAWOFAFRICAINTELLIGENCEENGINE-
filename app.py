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

# Safely initialize OpenAI Client using secrets
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception:
    st.warning("OpenAI API Key awaiting configuration.")
    client = None

# Safely initialize Database Connection
try:
    conn = st.connection("postgresql", type="sql")
except Exception:
    conn = None

# Base Knowledge Placeholder (Ensure legal_json is loaded if you have the file)
try:
    with open("legal_knowledge.json", "r") as file:
        legal_json = json.load(file)
except Exception:
    legal_json = "Base legal knowledge pending upload."

# 

# 2. AUTHENTICATION LOGIC (The Vault)
# 

try:
    # Pulling your secure credentials directly from st.secrets
    credentials = dict(st.secrets["credentials"])
    cookie = st.secrets["cookie"]
    
    authenticator = stauth.Authenticate(
        credentials,
        cookie["name"],
        cookie["key"],
        cookie["expiry_days"],
        st.secrets.get("preauthorized", {"emails": []})
    )
    
    # This is the exact line that was throwing the error earlier, now safely enclosed!
    authenticator.login(location="main")

except Exception as e:
    st.error("Authentication module awaiting configuration in st.secrets.")
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

# Only grant access if the user successfully logs in
if st.session_state.get("authentication_status"):
    
    # Capture the logged-in user's name for telemetry
    current_username = st.session_state["username"]
    
    # Sidebar Navigation
    with st.sidebar:
        st.write(f"Welcome, **{st.session_state['name']}**")
        active_node = st.radio("Navigation", ["Dashboard", "Chief Justice Telemetry 📊"])
        authenticator.logout("Logout", "sidebar")

    # 

    # 5. BIG DATA INGESTION (Chief Justice View)
    # 

    if active_node == "Chief Justice Telemetry 📊":
        st.title("📊 Chief Justice Telemetry")
        st.write("Secure infrastructure metrics and document ingestion.")

        # --- SECURE PDF UPLOADER ---
        st.subheader("📥 Dynamic Legal Ingestion Engine")
        st.write("Drag and drop legal PDFs here. The engine will instantly read and memorize the contents.")
        
        uploaded_file = st.file_uploader("Upload PDF Document", type=["pdf"])

        if uploaded_file is not None:
            try:
                # Instantly extract text from the PDF
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                extracted_text = ""
                for page in pdf_reader.pages:
                    extracted_text += page.extract_text() + "\n"
                
                # Assign extracted text to dynamic memory
                dynamic_memory = extracted_text

                system_directive = f"""
                BASE KNOWLEDGE: {legal_json}
                DYNAMIC UPLOADED MEMORY (PDF TEXT): {dynamic_memory}
                If the user asks about the uploaded document, use the DYNAMIC UPLOADED MEMORY to analyze it."""

                system_prompt = {"role": "system", "content": system_directive}

                # Initialize chat history if it doesn't exist yet
                if "messages" not in st.session_state:
                    st.session_state.messages = []

                # Render Chat History
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.write(message["content"])

                # User Input
                prompt = st.chat_input("Enter legal query or statute parameter...")

                if prompt:
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    with st.chat_message("user"):
                        st.write(prompt)

                    with st.chat_message("assistant"):
                        conversation_history = [system_prompt] + st.session_state.messages

                        try:
                            # LLM Call
                            if client:
                                response = client.chat.completions.create(
                                    model="llama-3.1-8b-instant",
                                    messages=conversation_history,
                                    temperature=0.1
                                )
                                engine_response = response.choices[0].message.content
                            else:
                                engine_response = "System Error: OpenAI Client is not connected. Check API keys."
                            
                            st.write(engine_response)
                            
                        except Exception as e:
                            engine_response = f"Cloud Execution Failure: {e}"
                            st.error(engine_response)

                    # Save AI response to memory
                    st.session_state.messages.append({"role": "assistant", "content": engine_response})

                    # --- BANDWIDTH TRACKING ---
                    if conn:
                        try:
                            with conn.session as s:
                                s.execute(text("UPDATE users SET query_count = query_count + 1 WHERE username = :u"), {"u": current_username})
                                s.commit()
                        except Exception as e:
                            st.error(f"Failed to update query telemetry: {e}")

                    st.rerun()

            except Exception as e:
                st.error(f"Failed to process PDF: {e}")
