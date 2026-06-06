import streamlit as st
import google.generativeai as genai
from google.oauth2 import service_account

# Secrets'tan anahtarı çek
api_key = st.secrets["GOOGLE_API_KEY"]

# Google'ın Service Account yetkilendirmesi için anahtarı yapılandır
# Not: Eğer AQ anahtarın doğrudan bir JSON içeriği değilse, 
# doğrudan API Key olarak yapılandırmayı deniyoruz:
genai.configure(api_key=api_key)

model = genai.GenerativeModel('gemini-1.5-flash')

st.title("🤖 ASLAN PARÇASI V8.9")

if prompt := st.chat_input("Reis bir şey de..."):
    st.chat_message("user").markdown(prompt)
    with st.chat_message("assistant"):
        try:
            response = model.generate_content(prompt)
            st.markdown(response.text)
        except Exception as e:
            # Buradaki hata detayını not al, hala hata veriyorsa başka bir yol deneyeceğiz
            st.error(f"Sistem Hatası: {e}")
