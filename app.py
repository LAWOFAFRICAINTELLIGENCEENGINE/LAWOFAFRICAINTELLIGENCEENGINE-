import streamlit as st
from groq import Groq
import google.generativeai as genai
from openai import OpenAI
import json
import pandas as pd

# 1. Infrastructure Config & CSS
st.set_page_config(page_title="Law of Africa & Universal Engine", page_icon="⚖️", layout="wide")

st.markdown("""
<style>
[data-testid="stChatInputSubmitButton"] {
    background-color: #1EBE55 !important;
    color: white !important;
    border-radius: 50% !important;
}
</style>
""", unsafe_allow_html=True)

# 2. Initialize State & Telemetry Trackers
if "messages" not in st.session_state:
    st.session_state.messages = []
if "query_count" not in st.session_state:
    st.session_state.query_count = 0 

# 3. Dynamic Knowledge Database (Law, History, & General)
knowledge_database = {
    "Customary Land Law": {"Category": "Legal", "Region": "West Africa", "Status": "Active Cache"},
    "Tribal Lineage Records": {"Category": "History", "Region": "Pan-Africa (500+ Yrs)", "Status": "Deep Cache Online"},
    "Universal Software/Coding": {"Category": "Engineering", "Region": "Global", "Status": "Unlimited Mode"},
    "General World Knowledge": {"Category": "General", "Region": "Global", "Status": "Active Cache"}
}
knowledge_json = json.dumps(knowledge_database, indent=2)

# 4. MASTER CONTROL (Simplified Sidebar)
with st.sidebar:
    st.title("🧠 Engine Control")
    st.write("The 3-Brain Super-System serves Lawyers, Engineers, and Everyday Users automatically.")
    
    st.divider()
    show_telemetry = st.toggle("📊 View Engine Telemetry")
    
    st.divider()
    if st.button("🗑️ Reset Engine Memory"):
        st.session_state.messages = []
        st.rerun()

# 5. ADMIN TELEMETRY DASHBOARD
if show_telemetry:
    st.title("📊 Engine Telemetry & Core Archives")
    st.write("Secure infrastructure metrics across Law, History, Code, and General queries.")
    
    col1, col2 = st.columns(2)
    col1.metric(label="Total Omni-Queries Processed", value=st.session_state.query_count)
    col2.metric(label="System Speed Latency", value="Optimal (Groq Accelerated)")
    
    st.divider()
    st.subheader("📜 Live Universal Knowledge Bases")
    df = pd.DataFrame.from_dict(knowledge_database, orient='index')
    st.dataframe(df, use_container_width=True)

# 6. UNIVERSAL SUPER-SYSTEM INTERFACE
else: 
    st.title("Law of Africa & Universal Intelligence Engine ⚖️🌍")
    st.caption("For Lawyers and Everyone Else. Solves Legal cases, 500+ Year History, Code, Math, and Everyday queries. Powered by Grok 4.5 + Gemini + Groq Llama 3.3.")
        
    # Render Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # User Input
    prompt = st.chat_input("Ask a legal problem, trace history, write code, or ask any general question...")

    if prompt:
        # Update Telemetry & Save User Prompt
        st.session_state.query_count += 1
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.write(prompt)
        
        with st.chat_message("assistant"):
            try:
                # 

                # STAGE 1: GROK (xAI) - THE DEEP RESEARCH & CONTEXT ENGINE
                # 

                with st.spinner("🔍 Brain 1 (Grok/xAI): Analyzing request and pulling deep context..."):
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

                    with st.expander("👁️ View Brain 1 (Grok) Context & Research"):
                        st.write(grok_context)

                # 

                # STAGE 2: GEMINI - THE SUPREME ROUTER & ARCHITECT
                # 

                with st.spinner("🏗️ Brain 2 (Gemini): Mapping the absolute master strategy..."):
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
                    
                    with st.expander("👁️ View Brain 2 (Gemini) Supreme Logic Blueprint"):
                        st.write(blueprint)
                
                # 

                # STAGE 3: GROQ - THE ULTRA-FAST EXECUTIVE PROBLEM SOLVER
                # 

                with st.spinner("⚡ Brain 3 (Groq): Executing final response at maximum speed and accuracy..."):
                    groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    
                    executor_system = "You are Brain 3, the Elite Executor AI. You operate with unlimited capacity. Read the Architect's strategy and generate the definitive final output. Be authoritative for law/history, technically flawless for code, and highly helpful for general queries. Do not leave placeholders."
                    executor_prompt = f"ARCHITECT'S STRATEGY:\n{blueprint}\n\nExecute this strategy perfectly and deliver the definitive final master output."
                    
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
