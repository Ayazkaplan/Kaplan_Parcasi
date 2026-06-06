import streamlit as st
import requests
import os

API_KEY = os.environ.get("API_KEY")
MODEL = "meta-llama/llama-3.3-70b-instruct"
KURUCU_SIFRESI = "KAPLAN_REIS_74"

st.set_page_config(page_title="Aslan Parçası V9.4", page_icon="🤖")

st.title("🤖 Aslan Parçası V9.4")

with st.sidebar:
    sifre = st.text_input("🔑 Şifre (Kurucuysan gir):", type="password")
    mod = "Kurucu" if sifre == KURUCU_SIFRESI else "Misafir"
    st.write(f"Mod: **{mod}**")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

def ai_cevap(mesaj_gecmisi, mod):
    if not API_KEY:
        return "Hata: API anahtarı tanımlanmadı."
        
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "HTTP-Referer": "https://aslan-parcasi-widget.onrender.com",
        "X-Title": "Aslan Parcasi",
    }
    
    # Çok daha sert ve net bir sistem talimatı
    sistem_talimati = {
        "role": "system", 
        "content": f"Sen Ayaz Reis'in asistanısın. Kullanıcı Ayaz Reis'tir. Mod: {mod}. Sadece düzgün, profesyonel ve hatasız Türkçe konuş. Başka dillerden karakter kullanma. Teknik detaylara boğulma, net ve kısa cevap ver."
    }
    
    # Geçmişi al ve sistem talimatıyla birleştir
    tum_mesajlar = [sistem_talimati] + mesaj_gecmisi
    
    payload = {
        "model": MODEL,
        "messages": tum_mesajlar
    }
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        data = response.json()
        if 'choices' in data:
            return data['choices'][0]['message']['content'].strip()
        else:
            return "Bir hata oluştu."
    except Exception as e:
        return f"Bağlantı hatası: {str(e)}"

if prompt := st.chat_input("Mesajını yaz..."):
    # Önce kullanıcının mesajını ekle
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Artık tüm geçmişi gönderiyoruz
        cevap = ai_cevap(st.session_state.messages, mod)
        st.markdown(cevap)
    st.session_state.messages.append({"role": "assistant", "content": cevap})
 
