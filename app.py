import streamlit as st
import requests
import os
import json
import firebase_admin
from firebase_admin import credentials, auth, firestore

# --- SAYFA AYARI (TEK SEFER) ---
st.set_page_config(page_title="Aslan Parçası V16.4", page_icon="🦁", layout="centered")

# --- AYARLAR ---
KURUCU_EMAIL = "ayazscma92@gmail.com"
MODEL = "anthropic/claude-3-haiku"
FIREBASE_API_KEY = os.environ.get("FIREBASE_API_KEY") 

# --- FIREBASE BAŞLATMA ---
if not firebase_admin._apps:
    try:
        secret_path = "/etc/secrets/firebase-key.json"
        local_path = "firebase-key.json"
        path_to_use = secret_path if os.path.exists(secret_path) else (local_path if os.path.exists(local_path) else None)
        with open(path_to_use, 'r') as f: 
            cred = credentials.Certificate(json.load(f))
            firebase_admin.initialize_app(cred)
    except Exception as e: 
        st.error(f"Firebase başlatılamadı: {e}"); st.stop()

db = firestore.client()

# --- OTURUM YÖNETİMİ ---
if "user_logged_in" not in st.session_state: st.session_state.user_logged_in = False
if "user_data" not in st.session_state: st.session_state.user_data = None
if "messages" not in st.session_state: st.session_state.messages = []
if "input_key" not in st.session_state: st.session_state.input_key = 0

# --- ŞİFRE KONTROLÜ (REST API) ---
def firebase_login(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    res = requests.post(url, json=payload)
    if res.status_code == 200:
        return res.json()
    else:
        return {"error": res.json().get('error', {}).get('message', 'Bilinmeyen Hata')}

# --- GİRİŞ VE KAYIT EKRANI ---
if not st.session_state.user_logged_in:
    st.title("🦁 Aslan Parçası V16.4")
    email = st.text_input("📧 E-posta:")
    password = st.text_input("🔑 Şifre:", type="password")
    isim_input = st.text_input("👤 Hesap İsmi:")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Giriş Yap"):
            auth_res = firebase_login(email, password)
            if auth_res and 'localId' in auth_res:
                user_doc = db.collection("users").document(auth_res['localId']).get()
                if user_doc.exists:
                    data = user_doc.to_dict()
                    if data.get("isim", "").strip() == isim_input.strip():
                        st.session_state.user_data = {**data, "uid": auth_res['localId']}
                        st.session_state.user_logged_in = True
                        st.rerun()
                    else: st.error("❌ Kayıtlı isim ile girdiğin isim eşleşmiyor!")
                else: st.error("❌ Kullanıcı hesabı bulunamadı!")
            else: st.error(f"❌ Giriş hatası: {auth_res.get('error', 'API Hatası')}")
    with col2:
        if st.button("Kayıt Ol"):
            try:
                user = auth.create_user(email=email, password=password)
                db.collection("users").document(user.uid).set({"isim": isim_input.strip(), "email": email, "videos": []})
                st.success("✅ Kayıt başarılı! Giriş yapabilirsin.")
            except Exception as e: st.error(f"❌ Hata: {e}")
    st.stop()

# --- ANA EKRAN ---
uid = st.session_state.user_data['uid']
user_ref = db.collection("users").document(uid)
user_doc = user_ref.get().to_dict()
gorunen_isim = user_doc.get('isim', 'Kullanıcı')
is_kurucu = user_doc.get('email') == KURUCU_EMAIL
rozet = " 🛠️" if is_kurucu else ""
saved_videos = user_doc.get("videos", [])

with st.sidebar:
    st.markdown(f"**👤 Profil:** {gorunen_isim}{rozet}")
    if st.button("🚪 Çıkış Yap"): st.session_state.clear(); st.rerun()
    st.divider()
    yeni_video = st.text_input("YouTube ID ekle:")
    if st.button("💾 Kaydet"):
        if yeni_video and yeni_video not in saved_videos:
            user_ref.update({"videos": firestore.ArrayUnion([yeni_video])}); st.rerun()
    for v in saved_videos:
        c1, c2 = st.columns([0.8, 0.2])
        c1.markdown(f'<iframe width="100%" height="150" src="https://www.youtube.com/embed/{v}" frameborder="0"></iframe>', unsafe_allow_html=True)
        if c2.button("🗑️", key=v):
            user_ref.update({"videos": firestore.ArrayRemove([v])}); st.rerun()

# --- STİL VE SOHBET ---
st.markdown("""<style>
    .assistant-box { background-color: rgba(30,30,30,0.9); padding: 15px; border-radius: 10px; border-left: 5px solid gold; margin-bottom: 15px; }
    .user-box { background-color: rgba(128,128,128,0.2); padding: 15px; border-radius: 10px; margin-bottom: 15px; text-align: right; }
    .header-box { font-weight: bold; margin-bottom: 5px; color: gold; }
    .user-header { color: #aaa; }
</style>""", unsafe_allow_html=True)

st.title("🤖 Aslan Parçası V16.4")

for m in st.session_state.messages:
    if m["role"] == "assistant":
        st.markdown(f'<div class="assistant-box"><div class="header-box">Aslan Parçası</div><div>{m["content"]}</div></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="user-box"><div class="header-box user-header">{gorunen_isim}</div><div>{m["content"]}</div></div>', unsafe_allow_html=True)

def ai_cevap(mesajlar):
    sistem_mesaji = f"Sen Aslan Parçası'sın. Kullanıcı: {gorunen_isim}. Nazik, profesyonel bir asistansın."
    payload = {"model": MODEL, "messages": [{"role": "system", "content": sistem_mesaji}] + mesajlar}
    headers = {"Authorization": f"Bearer {os.environ.get('API_KEY')}"}
    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        return res.json()['choices'][0]['message']['content']
    except: return "Sistem yorgun, Reis."

def send_message():
    val = st.session_state.my_input
    if val:
        st.session_state.messages.append({"role": "user", "content": val})
        cevap = ai_cevap(st.session_state.messages[-6:])
        st.session_state.messages.append({"role": "assistant", "content": cevap})
        st.session_state.my_input = "" 
        st.session_state.input_key += 1
        st.rerun()

st.text_area("Mesajını yaz:", key="my_input", height=100)
st.button("🚀 Gönder", on_click=send_message)
