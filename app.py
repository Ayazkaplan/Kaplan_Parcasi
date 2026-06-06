import streamlit as st
import requests
import json

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

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Reis bir şey de..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # HTTP isteği ile doğrudan API'ye bağlanıyoruz (SDK yok, kafa karışıklığı yok)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
        headers = {'Content-Type': 'application/json'}
        data = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response_json = response.json()
            
            if response.status_code == 200:
                answer = response_json['candidates'][0]['content']['parts'][0]['text']
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                st.error(f"Hata Kodu {response.status_code}: {response_json}")
                
        except Exception as e:
            st.error(f"Bağlantı Hatası: {e}")
