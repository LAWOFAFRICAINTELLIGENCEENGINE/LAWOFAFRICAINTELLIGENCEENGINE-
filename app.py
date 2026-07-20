import streamlit as st
from groq import Groq
import google.generativeai as genai
from openai import OpenAI
import PyPDF2
from PIL import Image
import io

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
</style>
""", unsafe_allow_html=True)

# 

# 2. LOGIN & SIGN-UP SYSTEM
# 

if "users_db" not in st.session_state:
    st.session_state.users_db = {
        "odogwucent001": {"password": "Tezla@@33CENT..", "is_vip": True, "full_name": "Emmanuel Paulinus", "email": "paulinusemmanuel634@gmail.com"}, 
        "guest": {"password": "123", "is_vip": False, "full_name": "Guest User", "email": "guest@test.com"}    
    }
if "current_user" not in st.session_state:
    st.session_state.current_user = None

if st.session_state.current_user is None:
    st.title("⚖️ Law of Africa & Universal Engine")
    st.write("Please log in or create an account to access the super-system.")
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
    
    with tab1:
        l_user = st.text_input("Username", key="l_user")
        l_pass = st.text_input("Password", type="password", key="l_pass")
        if st.button("Login", use_container_width=True):
            if l_user in st.session_state.users_db and st.session_state.users_db[l_user]["password"] == l_pass:
                st.session_state.current_user = l_user
                st.rerun()
            else:
                st.error("Invalid Username or Password.")
                
    with tab2:
        s_fullname = st.text_input("Full Name", key="s_fullname")
        s_email = st.text_input("Email Address", key="s_email")
        s_user = st.text_input("Choose a Username", key="s_user")
        s_pass = st.text_input("Choose a Password", type="password", key="s_pass")
        
        if st.button("Create Account", use_container_width=True):
            if s_user in st.session_state.users_db:
                st.error("Username already exists!")
            elif s_fullname and s_email and s_user and s_pass:
                st.session_state.users_db[s_user] = {"password": s_pass, "is_vip": False, "full_name": s_fullname, "email": s_email}
                st.success("Account created successfully! Switch to Login tab.")
            else:
                st.warning("Please fill out all fields.")

# 

# 3. MAIN UNIVERSAL INTERFACE
# 

else:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "query_count" not in st.session_state:
        st.session_state.query_count = 0 
        
    current_user = st.session_state.current_user
    is_vip = st.session_state.users_db[current_user]["is_vip"]
    display_name = st.session_state.users_db[current_user].get("full_name", current_user)

    with st.sidebar:
        st.title(f"Welcome, {display_name}!")
        if st.button("🚪 Logout"):
            st.session_state.current_user = None
            st.rerun()
        st.divider()
        if st.button("🗑️ Reset Engine Memory"):
            st.session_state.messages = []
            st.rerun()
        st.divider()
        if is_vip:
            st.success("💎 Premium Active")
        else:
            st.warning(f"🆓 Free Tier: {max(0, 3 - st.session_state.query_count)} Queries Left")

    st.title("Law of Africa & Universal Intelligence Engine ⚖️🌍")
    
    # Render Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if not is_vip and st.session_state.query_count >= 3:
        st.error("🔒 **FREE TRIAL EXPIRED** - Upgrade to Premium.")
    else:
        # File Uploader
        uploaded_files = st.file_uploader("📎 Upload PDFs or Images", accept_multiple_files=True, type=['pdf', 'png', 'jpg', 'jpeg'])
        prompt = st.chat_input("Ask a legal problem, trace history, write codes...")

        if prompt:
            st.session_state.query_count += 1
            
            # Display user message
            display_prompt = prompt
            if uploaded_files:
                display_prompt += f" [Attached {len(uploaded_files)} file(s)]"

            st.session_state.messages.append({"role": "user", "content": display_prompt})
            with st.chat_message("user"):
                st.write(display_prompt)
            
            with st.chat_message("assistant"):
                try:
                    # --- NEW: ACTUAL FILE PROCESSING ---
                    file_context = ""
                    if uploaded_files:
                        with st.spinner("📄 Reading attached files..."):
                            for file in uploaded_files:
                                if file.type == "application/pdf":
                                    pdf_reader = PyPDF2.PdfReader(file)
                                    text = "".join([page.extract_text() for page in pdf_reader.pages])
                                    file_context += f"\n--- PDF CONTENT: {file.name} ---\n{text[:6000]}\n"
                                elif file.type in ["image/png", "image/jpeg", "image/jpg"]:
                                    img = Image.open(file)
                                    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                                    llm = ChatGoogleGenerativeAI(model="gemini-flash")
                                    vis_resp = vision_model.generate_content(["Describe every detail of this image so I can analyze it:", img])
                                    file_context += f"\n--- IMAGE CONTENT: {file.name} ---\n{vis_resp.text}\n"
                    
                    # Combine prompt + files for the AI
                    active_prompt = prompt
                    if file_context:
                        active_prompt += f"\n\n[USER ATTACHED DOCUMENTS/IMAGES]:\n{file_context}"

                    # 🧠 STAGE 1: GROK
                    with st.spinner("🔍 Pulling deep context..."):
                        try:
                            xai_client = OpenAI(api_key=st.secrets["XAI_API_KEY"], base_url="https://api.x.ai/v1")
                            grok_response = xai_client.chat.completions.create(
                                model="grok-4.5",
                                messages=[{"role": "user", "content": active_prompt}],
                                max_tokens=1000
                            )
                            grok_context = grok_response.choices[0].message.content
                        except Exception:
                            grok_context = "Grok bypassed. Proceeding to Architect."

                    # 🧠 STAGE 2: GEMINI
                    with st.spinner("🏗️ Analyzing files & mapping strategy..."):
                        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                        llm = ChatGoogleGenerativeAI(model="gemini-flash")
                        blueprint = gemini_model.generate_content(f"USER PROMPT: {active_prompt}\nCONTEXT: {grok_context}\nDraft a logical blueprint to answer this.").text
                    
                    # 🧠 STAGE 3: GROQ
                    with st.spinner("⚡ Executing final response..."):
                        groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                        response = groq_client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[
                                {"role": "system", "content": "You are the Universal Engine. Execute the blueprint perfectly."},
                                {"role": "user", "content": f"BLUEPRINT:\n{blueprint}\n\nDeliver the final output for: {active_prompt}"}
                            ],
                            max_tokens=4000
                        )
                        final_output = response.choices[0].message.content
                    
                    st.write(final_output)
                    st.session_state.messages.append({"role": "assistant", "content": final_output})
                    
                except Exception as e:
                    # If an error happens, it will actually STAY on the screen now!
                    st.error(f"Engine Interruption! Error details: {str(e)}") 
