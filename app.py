import streamlit as st
import requests
import os
import json
import firebase_admin
from firebase_admin import credentials, auth
from duckduckgo_search import DDGS
from datetime import datetime, timedelta

# --- FIREBASE BAŞLATMA (GARANTİ YÖNTEM) ---
if not firebase_admin._apps:
    secret_path = "/etc/secrets/firebase-key.json"
    local_path = "firebase-key.json"
    
    # Render'daki secret dosyasını veya yerel dosyayı seç
    path_to_use = secret_path if os.path.exists(secret_path) else (local_path if os.path.exists(local_path) else None)
    
    if path_to_use:
        try:
            with open(path_to_use, 'r') as f:
                # JSON dosyasını sözlük olarak yükle (Invalid_grant'ı bu çözer)
                key_dict = json.load(f)
            cred = credentials.Certificate(key_dict)
            firebase_admin.initialize_app(cred)
        except Exception as e:
            st.error(f"Firebase başlatılamadı: {e}")
            st.stop()
    else:
        st.error("Firebase anahtarı bulunamadı! Lütfen Render Secret Files kısmını kontrol et.")

# --- AYARLAR ---
API_KEY = os.environ.get("API_KEY")
MODEL = "anthropic/claude-3-haiku"
NIHAI_SIFRE = "NiHAi_-kuRucU-AyAz"
DOSYA_ADI = "sarki_id.txt"
MOD_DOSYASI = "mod_id.txt"
ISIM_DOSYASI = "isim_id.txt"

# --- OTURUM YÖNETİMİ ---
if "user_logged_in" not in st.session_state: st.session_state.user_logged_in = False

def kaydet(dosya, deger):
    with open(dosya, "w") as f: f.write(deger.strip())

def oku(dosya):
    if os.path.exists(dosya):
        with open(dosya, "r") as f: return f.read().strip()
    return ""

def sil(dosya):
    if os.path.exists(dosya): os.remove(dosya)

def web_ara(sorgu):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(sorgu, max_results=3))
            return "Güncel bilgiler: " + "\n".join([r['body'] for r in results])
    except: return "İnternete erişemiyorum Reis."

# --- GİRİŞ EKRANI ---
if not st.session_state.user_logged_in:
    st.title("🦁 Aslan Parçası V16.4")
    email = st.text_input("📧 E-posta:")
    password = st.text_input("🔑 Şifre:", type="password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Giriş Yap"):
            try:
                auth.get_user_by_email(email)
                st.session_state.user_logged_in = True
                kaydet(MOD_DOSYASI, "Kurucu")
                st.rerun()
            except Exception as e: st.error(f"❌ Hata: {e}")
    with col2:
        if st.button("Kayıt Ol"):
            try:
                auth.create_user(email=email, password=password)
                st.success("✅ Kayıt başarılı!")
            except Exception as e: st.error(f"❌ Hata: {e}")
    st.stop()

st.set_page_config(page_title="Aslan Parçası V16.4", page_icon="🦁")

# --- MOD YÖNETİMİ ---
if "messages" not in st.session_state: st.session_state.messages = []
if "ayaz_yetkili" not in st.session_state: st.session_state.ayaz_yetkili = False

with st.sidebar:
    st.success("✅ Firebase Modu Aktif")
    if st.button("🚪 Çıkış Yap"): 
        sil(MOD_DOSYASI); sil(ISIM_DOSYASI); st.session_state.user_logged_in = False; st.rerun()
    
    kayitli_isim = oku(ISIM_DOSYASI) or "Mehmet Reis"
    secim = st.selectbox("👤 Kimsin Reis?", ["Mehmet Reis", "Ayaz Reis"], index=["Mehmet Reis", "Ayaz Reis"].index(kayitli_isim) if kayitli_isim in ["Mehmet Reis", "Ayaz Reis"] else 0)
    
    if secim == "Ayaz Reis":
        if not st.session_state.ayaz_yetkili:
            gizli_sifre = st.text_input("👑 Ayaz Reis Şifresi:", type="password")
            if st.button("Doğrula"):
                if gizli_sifre == NIHAI_SIFRE: st.session_state.ayaz_yetkili = True; kaydet(ISIM_DOSYASI, "Ayaz Reis"); st.rerun()
                else: st.error("❌ Hatalı Şifre!")
            isim = "Mehmet Reis"
        else: isim = "Ayaz Reis"
    else: st.session_state.ayaz_yetkili = False; kaydet(ISIM_DOSYASI, "Mehmet Reis"); isim = "Mehmet Reis"

    tema_secimi = st.selectbox("Arka Plan:", ["Aslan İni", "Kraliyet", "Uzay"])
    theme_map = {"Aslan İni": "#1a1a00", "Kraliyet": "#2c0000", "Uzay": "#1a0033"}
    bg_color = theme_map[tema_secimi]
    
    if st.button("🔄 Sohbeti Temizle"): st.session_state.messages = []; st.rerun()
    
    kayitli_id = oku(DOSYA_ADI)
    yeni_id = st.text_input("YouTube ID:", value=kayitli_id)
    if st.button("💾 Kaydet ve Oynat"): kaydet(DOSYA_ADI, yeni_id); st.rerun()
    if kayitli_id: st.markdown(f'<iframe width="100%" height="150" src="https://www.youtube.com/embed/{kayitli_id}" frameborder="0"></iframe>', unsafe_allow_html=True)

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
        cevap = ai_cevap(st.session_state.messages, isim, user_input)
        st.session_state.messages.append({"role": "assistant", "content": cevap})
        st.rerun()
