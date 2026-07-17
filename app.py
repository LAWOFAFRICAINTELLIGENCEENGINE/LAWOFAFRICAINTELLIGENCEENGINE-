# (Assuming this is inside your main try block)
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
        
        # if st.button("Create Account"): 
        # (The rest of your account creation logic goes here)


# ==========================================
# 6. BIG DATA INGESTION (Chief Justice View)
# ==========================================
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
            
            # (Assuming you map the extracted text to dynamic_memory here)

            system_directive = f"""
            BASE KNOWLEDGE: {legal_json}
            DYNAMIC UPLOADED MEMORY (PDF TEXT): {dynamic_memory}
            If the user asks about the uploaded document, use the DYNAMIC UPLOADED MEMORY to analyze it."""

            system_prompt = {"role": "system", "content": system_directive}

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

                # Save AI response to memory
                st.session_state.messages.append({"role": "assistant", "content": engine_response})

                # --- BANDWIDTH TRACKING ---
                try:
                    with conn.session as s:
                        s.execute(text("UPDATE users SET query_count = query_count + 1 WHERE username = :u"), {"u": current_username})
                        s.commit()
                except Exception as e:
                    st.error(f"Failed to update query telemetry: {e}")

                st.rerun()

        except Exception as e:
            st.error(f"Failed to process PDF: {e}")
