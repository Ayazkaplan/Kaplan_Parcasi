import streamlit as st
import google.generativeai as genai
import os

# Widget görünümü
st.set_page_config(page_title="Aslan Parçası", page_icon="🦁")
st.title("🦁 ASLAN PARÇASI V8.9")

# Secrets'tan anahtarı al
api_key = st.secrets["GOOGLE_API_KEY"]

# Service Account (AQ) anahtarı için yapılandırma
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Başlatma Hatası: {e}")

# Sohbet geçmişini tut
if "messages" not in st.session_state:
    st.session_state.messages = []

# Geçmişi ekrana bas
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Kullanıcı girişi
if prompt := st.chat_input("Reis bir şey de..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            response = model.generate_content(prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Hata: {e}")
