import streamlit as st
import requests
import os
import json
import firebase_admin
from firebase_admin import credentials, auth, firestore
from duckduckgo_search import DDGS
from datetime import datetime, timedelta

# --- FIREBASE BAŞLATMA ---
if not firebase_admin._apps:
    secret_path = "/etc/secrets/firebase-key.json"
    local_path = "firebase-key.json"
    path_to_use = secret_path if os.path.exists(secret_path) else (local_path if os.path.exists(local_path) else None)
    
    if path_to_use:
        with open(path_to_use, 'r') as f:
            key_dict = json.load(f)
        cred = credentials.Certificate(key_dict)
        firebase_admin.initialize_app(cred)
    else:
        st.error("Firebase anahtarı bulunamadı!")
        st.stop()

db = firestore.client()

# --- AYARLAR ---
API_KEY = os.environ.get("API_KEY")
MODEL = "anthropic/claude-3-haiku"
NIHAI_SIFRE = "NiHAi_-kuRucU-AyAz"

# --- OTURUM YÖNETİMİ ---
if "user_logged_in" not in st.session_state: st.session_state.user_logged_in = False
if "user_id" not in st.session_state: st.session_state.user_id = None
if "user_name" not in st.session_state: st.session_state.user_name = "Mehmet Reis"

def web_ara(sorgu):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(sorgu, max_results=3))
            return "Güncel bilgiler: " + "\n".join([r['body'] for r in results])
    except: return "İnternete erişemiyorum Reis."

# --- GİRİŞ & KAYIT EKRANI ---
if not st.session_state.user_logged_in:
    st.title("🦁 Aslan Parçası V16.4")
    email = st.text_input("📧 E-posta:")
    password = st.text_input("🔑 Şifre:", type="password")
    isim = st.text_input("👤 Kayıt Olacaksan İsmin:")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Giriş Yap"):
            try:
                user = auth.get_user_by_email(email)
                # Firestore'dan ismi çek
                user_doc = db.collection("users").document(user.uid).get()
                st.session_state.user_logged_in = True
                st.session_state.user_id = user.uid
                st.session_state.user_name = user_doc.to_dict().get("isim", "Mehmet Reis") if user_doc.exists else "Mehmet Reis"
                st.rerun()
            except Exception as e: st.error(f"❌ Hata: {e}")
    with col2:
        if st.button("Kayıt Ol"):
            try:
                user = auth.create_user(email=email, password=password)
                db.collection("users").document(user.uid).set({"isim": isim, "email": email})
                st.success("✅ Kayıt başarılı! Giriş yapabilirsin.")
            except Exception as e: st.error(f"❌ Hata: {e}")
    st.stop()

# --- ANA EKRAN ---
st.set_page_config(page_title="Aslan Parçası V16.4", page_icon="🦁")

if "messages" not in st.session_state: st.session_state.messages = []

with st.sidebar:
    st.success(f"✅ Hoş geldin, {st.session_state.user_name}")
    if st.button("🚪 Çıkış Yap"): 
        st.session_state.user_logged_in = False; st.rerun()
    
    tema_secimi = st.selectbox("Arka Plan:", ["Aslan İni", "Kraliyet", "Uzay"])
    theme_map = {"Aslan İni": "#1a1a00", "Kraliyet": "#2c0000", "Uzay": "#1a0033"}
    bg_color = theme_map[tema_secimi]
    
    if st.button("🔄 Sohbeti Temizle"): st.session_state.messages = []; st.rerun()

# --- STYLE ---
st.markdown(f"""<style>.stApp {{ background: linear-gradient(to bottom, {bg_color}, #000000); color: white; }} 
.assistant-box {{ background-color: rgba(30,30,30,0.9); padding: 15px; border-radius: 10px; border-left: 5px solid gold; margin-bottom: 10px; }} 
.user-box {{ background-color: rgba(128,128,128,0.2); padding: 15px; border-radius: 10px; margin-bottom: 10px; text-align: right; }}</style>""", unsafe_allow_html=True)

st.title("🤖 Aslan Parçası V16.4")

def ai_cevap(mesaj_gecmisi, isim, kullanici_mesaji):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    talimat = f"Sen Aslan Parçası'sın. {isim} ile konuşuyorsun. Saat: {(datetime.utcnow() + timedelta(hours=3)).strftime('%H:%M')}"
    if any(k in kullanici_mesaji.lower() for k in ["hava", "ara", "çevir"]): talimat += f" [İnternet]: {web_ara(kullanici_mesaji)}"
    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json={"model": MODEL, "messages": [{"role": "system", "content": talimat}] + mesaj_gecmisi[-6:]})
        return res.json()['choices'][0]['message']['content']
    except: return "Sistem meşgul, Reis."

for m in st.session_state.messages:
    if m["role"] == "assistant": st.markdown(f'<div class="assistant-box">{m["content"]}</div>', unsafe_allow_html=True)
    else: st.markdown(f'<div class="user-box">{m["content"]}</div>', unsafe_allow_html=True)

user_input = st.text_area("Mesajını yaz:", height=100)
if st.button("🚀 Gönder"):
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        cevap = ai_cevap(st.session_state.messages, st.session_state.user_name, user_input)
        st.session_state.messages.append({"role": "assistant", "content": cevap})
        st.rerun()
