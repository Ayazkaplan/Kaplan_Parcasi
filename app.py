import streamlit as st
import requests

API_KEY = "AIzaSyCZXEoUCgJCQN9dGJ1A-w4l_xbV1tqb_yY"

st.title("🤖 ASLAN PARÇASI - TANIYICI")

if st.button("Sistem Modellerini Listele"):
    # Doğrudan model listesini çekiyoruz, isim tahmin etmiyoruz
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
    
    response = requests.get(url)
    if response.status_code == 200:
        models = response.json().get('models', [])
        st.write("### Erişebildiğin Modeller:")
        for m in models:
            st.write(f"**Model Adı:** `{m['name']}`")
            st.write(f"Desteklenen metodlar: {m.get('supportedMethods', [])}")
            st.divider()
    else:
        st.error(f"Hata: {response.status_code} - {response.text}")
