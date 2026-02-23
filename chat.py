import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Gemini Chat", page_icon="💬")

st.title("💬 Gemini Chat (Streamlit Cloud)")

# ---------- API KEY (Streamlit Cloud best practice) ----------
# In Streamlit Cloud: Settings -> Secrets
# Add: GEMINI_API_KEY = "AIza...."
api_key = st.secrets.get("GEMINI_API_KEY", "")

if not api_key:
    st.error("GEMINI_API_KEY not found. Add it in Streamlit Cloud → App → Settings → Secrets.")
    st.stop()

# Clean any accidental newline characters
api_key = api_key.strip().replace("\r", "").replace("\n", "")
genai.configure(api_key=api_key)

# ---------- MODEL ----------
# If this model name fails, change it to one available in your account
MODEL_NAME = st.secrets.get("GEMINI_MODEL", "gemini-3-flash-preview")
model = genai.GenerativeModel(MODEL_NAME)

# ---------- SIDEBAR CONTROLS ----------
with st.sidebar:
    st.header("Settings")
    st.write(f"Model: `{MODEL_NAME}`")
    if st.button("🧹 Clear chat"):
        st.session_state.messages = []
        st.rerun()

# ---------- CHAT HISTORY ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ---------- CHAT INPUT ----------
user_text = st.chat_input("Type your question...")

def ask_gemini(history, prompt: str) -> str:
    """
    Sends conversation context + new prompt to Gemini.
    Gemini expects:
    contents = [{"role":"user","parts":[{"text":"..."}]}, {"role":"model","parts":[{"text":"..."}]}]
    In this SDK, use role 'model' for assistant responses.
    """
    contents = []
    for m in history:
        role = "user" if m["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": m["content"]}]})

    # Add the new user prompt
    contents.append({"role": "user", "parts": [{"text": prompt}]})

    resp = model.generate_content(contents)
    return resp.text

if user_text:
    # Save & show user message
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.write(user_text)

    # Generate assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                answer = ask_gemini(st.session_state.messages[:-1], user_text)
            except Exception as e:
                st.error(f"Error: {e}")
                st.stop()
            st.write(answer)

    # Save assistant message
    st.session_state.messages.append({"role": "assistant", "content": answer})