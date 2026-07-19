import streamlit as st
import streamlit_authenticator as stauth
from groq import Groq
import google.generativeai as genai
from openai import OpenAI
import json
import pandas as pd
import yaml
from yaml.loader import SafeLoader

# 

# 1. INFRASTRUCTURE & CSS
# 

st.set_page_config(page_title="Law of Africa & Universal Engine", page_icon="⚖️", layout="wide")

st.markdown("""
<style>
/* CUSTOM SEND BUTTON */
[data-testid="stChatInputSubmitButton"] {
    background-color: #1EBE55 !important;
    border-radius: 50% !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}
[data-testid="stChatInputSubmitButton"] svg { display: none !important; }
[data-testid="stChatInputSubmitButton"]::after {
    content: ''; display: inline-block; width: 20px; height: 20px;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M22 2L11 13' /%3E%3Cpath d='M22 2l-7 20-4-9-9-4 20-7z' /%3E%3Cpath d='M5 13l1 2 2 1-2 1-1 2-1-2-2-1 2-1 1-2z' fill='white' stroke='none' /%3E%3C/svg%3E");
    background-size: contain; background-repeat: no-repeat; background-position: center;
}

/* CUSTOM 3-DOTS MENU */
[data-testid="baseButton-header"] svg { display: none !important; }
[data-testid="baseButton-header"]::after {
    content: '\\22EE'; font-size: 26px; font-weight: bold; color: inherit;
    display: flex; align-items: center; justify-content: center; padding-bottom: 4px;
}
</style>
""", unsafe_allow_html=True)

# 

# 2. LOGIN & AUTHENTICATION SYSTEM
# 

# (Note: Replace this dummy dict with your actual DB/Users if needed)
credentials = {
    "usernames": {
        "emmanuel": {"email": "admin@lawofafrica.com", "name": "Emmanuel", "password": "abc", "is_vip": True},
        "guest": {"email": "guest@test.com", "name": "Guest User", "password": "123", "is_vip": False}
    }
}

authenticator = stauth.Authenticate(
    credentials,
    "law_of_africa_cookie",
    "abcdef",
    30
)

name, authentication_status, username = authenticator.login("main")

if authentication_status == False:
    st.error("Username/password is incorrect")
elif authentication_status == None:
    st.warning("Please enter your username and password to access the Engine.")
elif authentication_status:
    
    # 

    # 3. INITIALIZE SESSION STATE & PAYWALL
    # 

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "query_count" not in st.session_state:
        st.session_state.query_count = 0 
    
    # Check VIP status from credentials
    is_vip = credentials["usernames"][username].get("is_vip", False)

    # 

    # 4. SIDEBAR & TELEMETRY
    # 

    with st.sidebar:
        st.title(f"Welcome, {name}")
        authenticator.logout("Logout", "sidebar")
        st.divider()
        st.title("⚙️ Engine Control")
        st.toggle("📊 View Engine Telemetry", key="show_telemetry")
        st.divider()
        if st.button("🗑️ Reset Engine Memory"):
            st.session_state.messages = []
            st.session_state.query_count = 0
            st.rerun()
            
        st.divider()
        if is_vip:
            st.success("💎 VIP Premium Active: Unlimited Queries")
        else:
            queries_left = max(0, 3 - st.session_state.query_count)
            st.warning(f"🆓 Free Tier: {queries_left} Queries Remaining")

    # 

    # 5. MAIN UNIVERSAL INTERFACE
    # 

    if st.session_state.get("show_telemetry", False):
        st.title("📊 Engine Telemetry & Core Archives")
        col1, col2 = st.columns(2)
        col1.metric("Total Omni-Queries", st.session_state.query_count)
        col2.metric("System Latency", "Optimal")
    else:
        st.title("Law of Africa & Universal Intelligence Engine ⚖️🌍")
        
        # Render Chat History
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        # Check Paywall BEFORE showing input
        if not is_vip and st.session_state.query_count >= 3:
            st.error("🔒 **FREE TRIAL EXPIRED**")
            st.write("You have used your 3 free queries. Please upgrade to a Monthly or Yearly VIP Premium Subscription to unlock the Universal Intelligence Engine.")
            st.button("💳 Upgrade to VIP Premium Now")
        else:
            # File Uploader
            uploaded_files = st.file_uploader("📎 Upload PDFs or Images", accept_multiple_files=True, type=['pdf', 'png', 'jpg', 'jpeg'])

            # Chat Input
            prompt = st.chat_input("Ask a legal problem, trace history, write code...")

            if prompt:
                st.session_state.query_count += 1
                
                full_prompt = prompt
                if uploaded_files:
                    full_prompt += f" [Attached {len(uploaded_files)} file(s)]"

                st.session_state.messages.append({"role": "user", "content": full_prompt})
                with st.chat_message("user"):
                    st.write(full_prompt)
                
                with st.chat_message("assistant"):
                    try:
                        # 🧠 STAGE 1: GROK (Context)
                        with st.spinner("🔍 Pulling deep context..."):
                            try:
                                xai_client = OpenAI(api_key=st.secrets["XAI_API_KEY"], base_url="https://api.x.ai/v1")
                                grok_response = xai_client.chat.completions.create(
                                    model="grok-4.5",
                                    messages=[{"role": "system", "content": "Analyze the user's prompt deeply."}, {"role": "user", "content": prompt}],
                                    max_tokens=1000
                                )
                                grok_context = grok_response.choices[0].message.content
                            except Exception:
                                grok_context = "Grok bypassed. Proceeding to Architect."

                        # 🧠 STAGE 2: GEMINI (Blueprint)
                        with st.spinner("🏗️ Mapping master strategy..."):
                            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                            gemini_model = genai.GenerativeModel('gemini-1.5-pro')
                            blueprint = gemini_model.generate_content(f"USER: {prompt}\nCONTEXT: {grok_context}\nDraft a logical blueprint to answer this.").text
                        
                        # 🧠 STAGE 3: GROQ (Final Execution)
                        with st.spinner("⚡ Executing final response..."):
                            groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                            response = groq_client.chat.completions.create(
                                model="llama-3.3-70b-versatile",
                                messages=[
                                    {"role": "system", "content": "You are the Law of Africa Universal Engine. Execute the blueprint perfectly."},
                                    {"role": "user", "content": f"BLUEPRINT:\n{blueprint}\n\nDeliver the final output for: {prompt}"}
                                ],
                                max_tokens=4000
                            )
                            final_output = response.choices[0].message.content
                        
                        st.write(final_output)
                        st.session_state.messages.append({"role": "assistant", "content": final_output})
                        
                    except Exception as e:
                        st.error(f"Engine Interruption. Please check your API keys in Streamlit secrets! Error: {str(e)}")
                        
                st.rerun() 
