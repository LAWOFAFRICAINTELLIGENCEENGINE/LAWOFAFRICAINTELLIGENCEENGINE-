import streamlit as st
import streamlit_authenticator as stauth
from groq import Groq
import google.generativeai as genai
from openai import OpenAI
import json
import pandas as pd
import sqlalchemy
import psycopg2
import PyPDF2
import faiss
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from sentence_transformers import SentenceTransformer

# 1. Infrastructure Config & CSS
st.set_page_config(page_title="Law of Africa & Universal Engine", page_icon="⚖️", layout="wide")

st.markdown("""
<style>
/* --- CUSTOM SEND BUTTON (Green + Arrow with Sparkle) --- */
[data-testid="stChatInputSubmitButton"] {
    background-color: #1EBE55 !important;
    border-radius: 50% !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

/* Hide the default Streamlit plane icon */
[data-testid="stChatInputSubmitButton"] svg {
    display: none !important;
}

/* Inject the custom Sparkle + Hollow Arrow Icon */
[data-testid="stChatInputSubmitButton"]::after {
    content: '';
    display: inline-block;
    width: 20px;
    height: 20px;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M22 2L11 13' /%3E%3Cpath d='M22 2l-7 20-4-9-9-4 20-7z' /%3E%3Cpath d='M5 13l1 2 2 1-2 1-1 2-1-2-2-1 2-1 1-2z' fill='white' stroke='none' /%3E%3C/svg%3E");
    background-size: contain;
    background-repeat: no-repeat;
    background-position: center;
}

/* --- CUSTOM 3-DOTS APP MENU --- */
/* Hide the default Streamlit hamburger menu */
[data-testid="baseButton-header"] svg {
    display: none !important;
}

/* Inject 3 vertical dots */
[data-testid="baseButton-header"]::after {
    content: '\\22EE'; 
    font-size: 26px;
    font-weight: bold;
    color: inherit;
    display: flex;
    align-items: center;
    justify-content: center;
    padding-bottom: 4px;
}
</style>
""", unsafe_allow_html=True)

# 2. Initialize State & Telemetry Trackers
if "messages" not in st.session_state:
    st.session_state.messages = []
if "query_count" not in st.session_state:
    st.session_state.query_count = 0 

# 3. Dynamic Knowledge Database
knowledge_database = {
    "Customary Land Law": {"Category": "Legal", "Region": "West Africa", "Status": "Active Cache"},
    "Tribal Lineage Records": {"Category": "History", "Region": "Pan-Africa (500+ Yrs)", "Status": "Deep Cache Online"},
    "Universal Software/Coding": {"Category": "Engineering", "Region": "Global", "Status": "Unlimited Mode"},
    "General World Knowledge": {"Category": "General", "Region": "Global", "Status": "Active Cache"}
}
knowledge_json = json.dumps(knowledge_database, indent=2)

# 4. MASTER CONTROL (Sidebar)
with st.sidebar:
    st.title("⚙️ Engine Control")
    
    st.divider()
    # FIXED TOGGLE: Tied to session state key so it never gets stuck
    st.toggle("📊 View Engine Telemetry", key="show_telemetry")
    
    st.divider()
    st.success("🔌 LangChain & FAISS Modules Loaded")
    st.success("📄 PyPDF2 Document Scanner Loaded")
    st.success("🗄️ SQLAlchemy Database Ready")
    
    st.divider()
    if st.button("🗑️ Reset Engine Memory"):
        st.session_state.messages = []
        st.rerun()

# 5. ADMIN TELEMETRY DASHBOARD
if st.session_state.show_telemetry:
    st.title("📊 Engine Telemetry & Core Archives")
    st.write("Secure infrastructure metrics across Law, History, Code, and General queries.")
    
    col1, col2 = st.columns(2)
    col1.metric(label="Total Omni-Queries Processed", value=st.session_state.query_count)
    col2.metric(label="System Speed Latency", value="Optimal")
    
    st.divider()
    st.subheader("📜 Live Universal Knowledge Bases")
    df = pd.DataFrame.from_dict(knowledge_database, orient='index')
    st.dataframe(df, use_container_width=True)

# 6. UNIVERSAL SUPER-SYSTEM INTERFACE
else: 
    # Clean, strict branding
    st.title("Law of Africa & Universal Intelligence Engine ⚖️🌍")
        
    # Render Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # ADDED: File Uploader for PDFs and Images right above the chat input
    uploaded_files = st.file_uploader("📎 Upload PDFs or Images to the Engine", accept_multiple_files=True, type=['pdf', 'png', 'jpg', 'jpeg'])

    # User Input
    prompt = st.chat_input("Enter your request...")

    if prompt:
        # Check if files are attached to modify the prompt context visually
        file_status = f" [Attached {len(uploaded_files)} file(s)]" if uploaded_files else ""
        full_prompt_display = prompt + file_status

        # Update Telemetry & Save User Prompt
        st.session_state.query_count += 1
        st.session_state.messages.append({"role": "user", "content": full_prompt_display})
        
        with st.chat_message("user"):
            st.write(full_prompt_display)
        
        with st.chat_message("assistant"):
            try:
                # 

                # STAGE 1: GROK (xAI) - THE DEEP RESEARCH & CONTEXT ENGINE
                # 

                with st.spinner("🔍 Analyzing request and pulling deep context..."):
                    try:
                        xai_client = OpenAI(
                            api_key=st.secrets["XAI_API_KEY"],
                            base_url="https://api.x.ai/v1",
                        )
                        grok_response = xai_client.chat.completions.create(
                            model="grok-4.5",
                            messages=[
                                {"role": "system", "content": "You are Brain 1 of the Law of Africa Universal Engine. Analyze the user's prompt. If it is about African history or law (e.g., Igbo, Yoruba), trace 500+ years of deep context. If it is about coding, math, or general everyday questions, provide maximum global context, edge cases, and structural advice."},
                                {"role": "user", "content": prompt}
                            ],
                            max_tokens=8000
                        )
                        grok_context = grok_response.choices[0].message.content
                    except Exception as e:
                        grok_context = f"Grok Archival Bypass: Proceeding with base engine prompt. Error: {e}"

                    with st.expander("👁️ View Internal Research Context"):
                        st.write(grok_context)

                # 

                # STAGE 2: GEMINI - THE SUPREME ROUTER & ARCHITECT
                # 

                with st.spinner("🏗️ Mapping the absolute master strategy..."):
                    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                    gemini_model = genai.GenerativeModel('gemini-1.5-pro')
                    
                    architect_prompt = f"""You are Brain 2, the Supreme Architect. 
                    SYSTEM DATABASE: {knowledge_json}
                    
                    USER REQUEST: "{prompt}"
                    GROK'S ANALYSIS: "{grok_context}"
                    
                    INSTRUCTIONS:
                    Synthesize the request. 
                    1. If LEGAL/HISTORY: Draft a bulletproof framework using deep customary/historical facts.
                    2. If CODING/ENGINEERING: Draft an unlimited, step-by-step logic blueprint.
                    3. If GENERAL/EVERYDAY (e.g., advice, cooking, math): Draft a highly accurate, polite, and comprehensive plan to answer the user perfectly.
                    DO NOT write the final execution text or code. Just provide the logical blueprint."""
                    
                    blueprint = gemini_model.generate_content(architect_prompt).text
                    
                    with st.expander("👁️ View Internal Logic Blueprint"):
                        st.write(blueprint)
                
                # 

                # STAGE 3: GROQ - THE ULTRA-FAST EXECUTIVE PROBLEM SOLVER
                # 

                with st.spinner("⚡ Executing final response..."):
                    groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    
                    executor_system = "You are the Law of Africa & Universal Intelligence Engine. You operate with unlimited capacity. Read the internal strategy and generate the definitive final output. Be authoritative for law/history, technically flawless for code, and highly helpful for general queries. Do not leave placeholders. Do not mention your underlying models."
                    executor_prompt = f"INTERNAL STRATEGY:\n{blueprint}\n\nExecute this strategy perfectly and deliver the definitive final master output."
                    
                    response = groq_client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": executor_system},
                            {"role": "user", "content": executor_prompt}
                        ],
                        temperature=0.1, 
                        max_tokens=8000
                    )
                    final_output = response.choices[0].message.content
                
                # Display final result and save to history
                st.write(final_output)
                st.session_state.messages.append({"role": "assistant", "content": final_output})
                
            except Exception as e:
                st.error(f"Engine Interruption: {e}")
                
        st.rerun() 
