import streamlit as st
from google import genai
from google.genai import types

# API Anahtarın
API_KEY = "AIzaSyCZXEoUCgJCQN9dGJ1A-w4l_xbV1tqb_yY"

st.set_page_config(page_title="ASLAN PARÇASI", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0b0d17; color: white; }
    h1 { color: #deff9a; text-align: center; }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 ASLAN PARÇASI V8.9")

# Hafıza Yönetimi
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mesajları Ekrana Bas
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Kullanıcı Girişi
if prompt := st.chat_input("Reis bir şey de..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Client oluşturma
        client = genai.Client(api_key=API_KEY)
        
        # Geçmiş hafızayı al
        gecmis_metin = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-10:]])
        
        config = types.GenerateContentConfig(
            system_instruction=f"Geçmiş sohbet:\n{gecmis_metin}\n\nSen bir Aslan Parçası'sın, delikanlıca cevap ver.",
            temperature=0.7
        )
        
        try:
            # Model ismini doğrudan 'gemini-1.5-flash' olarak kullanıyoruz
            response = client.models.generate_content(
                model="gemini-1.5-flash", 
                contents=prompt,
                config=config
            )
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Hata oluştu reis: {e}")
