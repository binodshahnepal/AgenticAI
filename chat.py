import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Gemini Chat", page_icon="💬")
st.title("💬 Gemini Chat (Streamlit Cloud)")

# ---------------- API KEY (Secrets ONLY) ----------------
# Streamlit Cloud -> Manage app -> Settings -> Secrets:
# GEMINI_API_KEY = "YOUR_KEY"
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("GEMINI_API_KEY not found. Add it in Streamlit Cloud → Manage app → Settings → Secrets.")
    st.info('Example:\n\nGEMINI_API_KEY = "AIza..."\nGEMINI_MODEL = "gemini-3-flash-preview"')
    st.stop()

# Clean any accidental whitespace/newlines
api_key = api_key.strip().replace("\r", "").replace("\n", "")
genai.configure(api_key=api_key)

# ---------------- MODEL ----------------
MODEL_NAME = st.secrets.get("GEMINI_MODEL", "gemini-3-flash-preview")

# Sidebar controls
with st.sidebar:
    st.header("Settings")
    st.write(f"Model: `{MODEL_NAME}`")

    if st.button("🧹 Clear chat"):
        st.session_state.messages = []
        st.rerun()

    # Optional: Model debug helper
    with st.expander("🔎 List available models (debug)"):
        try:
            models = []
            for m in genai.list_models():
                if "generateContent" in getattr(m, "supported_generation_methods", []):
                    models.append(m.name)
            if models:
                st.write("Models that support generateContent:")
                st.code("\n".join(models))
            else:
                st.write("No generateContent-capable models found for this API key.")
        except Exception as e:
            st.error(f"Could not list models: {e}")

# Build model object (some environments prefer 'models/...' prefix)
try:
    model = genai.GenerativeModel(MODEL_NAME)
except Exception:
    # fallback attempt with 'models/' prefix if user provided short name
    if not MODEL_NAME.startswith("models/"):
        model = genai.GenerativeModel(f"models/{MODEL_NAME}")
    else:
        raise

# ---------------- CHAT HISTORY ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ---------------- CHAT INPUT ----------------
user_text = st.chat_input("Type your question...")

def ask_gemini(history, prompt: str) -> str:
    """
    Send conversation history + new prompt to Gemini.
    Stream format:
      user  -> role="user"
      assistant -> role="model"
    """
    contents = []
    for m in history:
        role = "user" if m["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": m["content"]}]})

    contents.append({"role": "user", "parts": [{"text": prompt}]})

    resp = model.generate_content(contents)
    return resp.text

if user_text:
    # Save user message
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.write(user_text)

    # Generate assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                answer = ask_gemini(st.session_state.messages[:-1], user_text)
                st.write(answer)
            except Exception as e:
                st.error(f"Error calling Gemini: {e}")
                st.stop()

    # Save assistant message
    st.session_state.messages.append({"role": "assistant", "content": answer})
