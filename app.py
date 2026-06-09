import streamlit as st
import requests
import os
import json
import firebase_admin
from firebase_admin import credentials, auth, firestore
import re

# --- AYARLAR ---
KURUCU_EMAIL = "ayazscma92@gmail.com"
MODEL = "anthropic/claude-3-haiku"
AVATAR_URL = "https://i.imgur.com/3EfO8Ae.jpeg"
USER_AVATAR = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
FIREBASE_API_KEY = os.environ.get("FIREBASE_API_KEY") 

# --- FIREBASE BAŞLATMA ---
if not firebase_admin._apps:
    secret_path = "/etc/secrets/firebase-key.json"
    local_path = "firebase-key.json"
    path_to_use = secret_path if os.path.exists(secret_path) else (local_path if os.path.exists(local_path) else None)
    if path_to_use:
        with open(path_to_use, 'r') as f: cred = credentials.Certificate(json.load(f))
        firebase_admin.initialize_app(cred)
    else: st.error("Firebase anahtarı bulunamadı!"); st.stop()

db = firestore.client()

# --- OTURUM YÖNETİMİ ---
if "user_logged_in" not in st.session_state: st.session_state.user_logged_in = False
if "user_data" not in st.session_state: st.session_state.user_data = None
if "messages" not in st.session_state: st.session_state.messages = []

# --- ŞİFRE KONTROLÜ (REST API) ---
def firebase_login(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    res = requests.post(url, json=payload)
    return res.json() if res.status_code == 200 else None

# --- EMOJİ KONTROLÜ ---
def emoji_var_mi(text):
    return bool(re.search(r'[^\w\s,.]', text))

# --- GİRİŞ VE KAYIT EKRANI ---
if not st.session_state.user_logged_in:
    st.set_page_config(page_title="Aslan Parçası V16.4", page_icon="🦁")
    st.title("🦁 Aslan Parçası V16.4")
    email = st.text_input("📧 E-posta:")
    password = st.text_input("🔑 Şifre:", type="password")
    isim_input = st.text_input("👤 Hesap İsmi:")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Giriş Yap"):
            auth_res = firebase_login(email, password)
            if auth_res:
                user_doc = db.collection("users").document(auth_res['localId']).get()
                if user_doc.exists and user_doc.to_dict().get("isim") == isim_input:
                    st.session_state.user_data = {**user_doc.to_dict(), "uid": auth_res['localId']}
                    st.session_state.user_logged_in = True
                    st.rerun()
                else: st.error("❌ İsim veya bilgiler hatalı!")
            else: st.error("❌ E-posta veya şifre yanlış!")
    with col2:
        if st.button("Kayıt Ol"):
            try:
                user = auth.create_user(email=email, password=password)
                db.collection("users").document(user.uid).set({"isim": isim_input, "email": email, "videos": []})
                st.success("✅ Kayıt başarılı!")
            except Exception as e: st.error(f"❌ Hata: {e}")
    st.stop()

# --- ANA EKRAN AYARLARI ---
st.set_page_config(page_title="Aslan Parçası V16.4", page_icon="🦁", layout="centered")

uid = st.session_state.user_data['uid']
user_ref = db.collection("users").document(uid)
user_doc = user_ref.get().to_dict()
is_kurucu = user_doc.get('email') == KURUCU_EMAIL
saved_videos = user_doc.get("videos", [])

# --- SİDEBAR & PROFİL DÜZENLEME ---
with st.sidebar:
    st.markdown("### 👤 Profil Ayarları")
    yeni_isim = st.text_input("Yeni İsim:", value=user_doc.get('isim'))
    
    if st.button("İsmi Güncelle"):
        if not is_kurucu and emoji_var_mi(yeni_isim):
            st.warning("⚠️ İsminizde emoji kullanamazsınız.")
        else:
            user_ref.update({"isim": yeni_isim})
            st.success("✅ İsim güncellendi!")
            st.rerun()
            
    # Kurucu İsmi Parlak Tasarımı
    gorunen_isim = user_doc.get('isim')
    if is_kurucu:
        isim_stili = f'<span style="color:red; font-weight:bold; text-shadow: 0 0 8px red;">{gorunen_isim} 🛠️</span>'
    else:
        isim_stili = gorunen_isim

    st.markdown(f"**Profil:** {isim_stili}", unsafe_allow_html=True)
    
    if st.button("🧹 Sohbeti Temizle"):
        st.session_state.messages = []
        st.rerun()
        
    if st.button("🚪 Çıkış Yap"): st.session_state.clear(); st.rerun()
    
    st.divider()
    yeni_video = st.text_input("YouTube ID ekle:")
    if st.button("💾 Kaydet"):
        if yeni_video and yeni_video not in saved_videos:
            user_ref.update({"videos": firestore.ArrayUnion([yeni_video])})
            st.rerun()
    
    for v in saved_videos:
        c1, c2 = st.columns([0.8, 0.2])
        c1.markdown(f'<iframe width="100%" height="150" src="https://www.youtube.com/embed/{v}" frameborder="0"></iframe>', unsafe_allow_html=True)
        if c2.button("🗑️", key=v):
            user_ref.update({"videos": firestore.ArrayRemove([v])})
            st.rerun()

# --- STYLE VE SOHBET ---
st.markdown("""<style>
    .assistant-box { background-color: rgba(30,30,30,0.9); padding: 15px; border-radius: 10px; border-left: 5px solid gold; margin-bottom: 15px; display: flex; align-items: flex-start; gap: 10px; }
    .user-box { background-color: rgba(128,128,128,0.2); padding: 15px; border-radius: 10px; margin-bottom: 15px; display: flex; justify-content: flex-end; align-items: flex-start; gap: 10px; }
    .avatar { width: 40px; height: 40px; border-radius: 50%; }
    .header-box { display: flex; align-items: center; gap: 10px; font-weight: bold; margin-bottom: 5px; }
</style>""", unsafe_allow_html=True)

st.title("🤖 Aslan Parçası V16.4")

for m in st.session_state.messages:
    if m["role"] == "assistant":
        st.markdown(f'''<div class="assistant-box"><img src="{AVATAR_URL}" class="avatar"><div><div class="header-box">Aslan Parçası</div><div>{m["content"]}</div></div></div>''', unsafe_allow_html=True)
    else:
        display_name = f'<span style="color:red; text-shadow: 0 0 5px red;">{user_doc.get("isim")} 🛠️</span>' if is_kurucu else user_doc.get("isim")
        st.markdown(f'''<div class="user-box"><div><div class="header-box" style="justify-content: flex-end;">{display_name}</div><div>{m["content"]}</div></div><img src="{USER_AVATAR}" class="avatar"></div>''', unsafe_allow_html=True)

def ai_cevap(mesajlar):
    sistem_mesaji = f"Sen Aslan Parçası'sın. Kurucun Ayaz Kaplan. Nazik, profesyonel bir asistansın. Her zaman kendini 'Aslan Parçası' olarak tanıt."
    payload = {"model": MODEL, "messages": [{"role": "system", "content": sistem_mesaji}] + mesajlar}
    headers = {"Authorization": f"Bearer {os.environ.get('API_KEY')}"}
    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        return res.json()['choices'][0]['message']['content']
    except: return "Sistem yorgun, Reis."

if "input_key" not in st.session_state: st.session_state.input_key = 0

def send_message():
    val = st.session_state.my_input
    if val:
        st.session_state.messages.append({"role": "user", "content": val})
        cevap = ai_cevap(st.session_state.messages[-6:])
        st.session_state.messages.append({"role": "assistant", "content": cevap})
        st.session_state.my_input = "" 
        st.session_state.input_key += 1

st.text_area("Mesajını yaz:", key="my_input", height=100)
st.button("🚀 Gönder", on_click=send_message)
