import streamlit as st
import google.generativeai as genai
import datetime

# --- 1. Page Config ---
st.set_page_config(page_title="F8 Chatbot AI", page_icon="🤖", layout="wide")

# --- 2. Custom CSS Loader ---
def load_css(dark_mode=False):
    if dark_mode:
        st.markdown(
            """
            <style>
            /* Main App */
            .stApp {
                background-color: #121212 !important;
                color: #ffffff !important;
            }

            /* Chat Bubbles */
            .chat-user {
                background-color: #1e88e5 !important;
                color: #ffffff !important;
                padding: 10px;
                border-radius: 12px;
                margin: 5px 0;
                max-width: 80%;
                align-self: flex-end;
            }
            .chat-bot {
                background-color: #1e1e1e !important;
                color: #ffffff !important;
                padding: 10px;
                border-radius: 12px;
                margin: 5px 0;
                max-width: 80%;
                align-self: flex-start;
            }

            /* Notification Boxes */
            div[data-testid="stNotification"] p {
                color: #ffffff !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <style>
            .stApp {
                background-color: #ffffff !important;
                color: #000000 !important;
            }
            .chat-user {
                background-color: #1976d2 !important;
                color: #ffffff !important;
                padding: 10px;
                border-radius: 12px;
                margin: 5px 0;
                max-width: 80%;
                align-self: flex-end;
            }
            .chat-bot {
                background-color: #f1f1f1 !important;
                color: #000000 !important;
                padding: 10px;
                border-radius: 12px;
                margin: 5px 0;
                max-width: 80%;
                align-self: flex-start;
            }
            div[data-testid="stNotification"] p {
                color: #000000 !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

# --- 2. UI Title ---
st.title("F8 Chatbot AI")
st.caption("Powered by Google's Gemini API | Enhanced with Streamlit")

# --- 3. Sidebar ---
with st.sidebar:
    st.subheader("⚙️ Settings")
    
    # API Key
    google_api_key = st.text_input("Google AI API Key", type="password")
    
    # Model Selection
    model_choice = st.selectbox(
        "Choose Model", 
        ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.5-flash", "gemini-2.5-pro"]
    )
    
    # Creativity
    temperature = st.slider("Creativity (temperature)", 0.0, 1.0, 0.7, 0.1)
    
    # Token Limit
    max_tokens = st.slider("Max Tokens", 100, 2048, 512, 50)
    
    # System Role
    system_role = st.text_area(
        "System Role (Persona)", 
        "You are a friendly AI assistant that helps the user."
    )
    
    # Dark Mode Switch
    dark_mode = st.toggle("🌙 Dark Mode", value=False)
    load_css(dark_mode)

    # Reset Chat
    reset_button = st.button("♻️ Reset Conversation")

    # Download Chat History
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if st.button("💾 Download Chat History"):
        if st.session_state.messages:
            chat_history = ""
            for msg in st.session_state.messages:
                timestamp = msg.get("time", "")
                chat_history += f"[{timestamp}] {msg['role'].capitalize()}: {msg['content']}\n\n"

            file_name = f"chat_history_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            st.download_button(
                label="⬇️ Save as TXT",
                data=chat_history,
                file_name=file_name,
                mime="text/plain"
            )
        else:
            st.warning("Belum ada chat untuk disimpan!")

# --- 4. API Setup ---
if not google_api_key:
    st.info("🔑 Please enter your API key to start chatting.")
    st.stop()

genai.configure(api_key=google_api_key)

# --- 5. Session State ---
if "chat" not in st.session_state or reset_button:
    st.session_state.chat = genai.GenerativeModel(model_choice).start_chat(history=[])
    st.session_state.messages = []

# --- 7. Chat Input ---
user_input = st.chat_input("Type your message...")

if user_input:
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    st.session_state.messages.append({"role": "user", "content": user_input, "time": timestamp})

    response = st.session_state.chat.send_message(
        user_input,
        generation_config={"temperature": temperature, "max_output_tokens": max_tokens}
    )
    bot_reply = response.candidates[0].content.parts[0].text

    st.session_state.messages.append({"role": "bot", "content": bot_reply, "time": timestamp})

# --- 8. Display Chat ---
for msg in st.session_state.messages:
    role_class = "chat-user" if msg["role"] == "user" else "chat-bot"
    st.markdown(
        f"""
        <div class="{role_class}">
            <b>{msg['role'].capitalize()} [{msg['time']}]:</b><br>
            {msg['content']}
        </div>
        """,
        unsafe_allow_html=True
    )

# Auto-scroll to latest message
st.markdown("<script>window.scrollTo(0, document.body.scrollHeight);</script>", unsafe_allow_html=True)
