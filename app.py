import streamlit as st
import requests
import os

# Ayarlar
API_KEY = os.environ.get("API_KEY")
MODEL = "anthropic/claude-3-haiku"
KURUCU_SIFRESI = "KAPLAN_REIS_74"
AVATAR_URL = "https://i.imgur.com/3EfO8Ae.jpeg"
USER_AVATAR = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

# Versiyon V11.5 olarak güncellendi
st.set_page_config(page_title="Aslan Parçası V11.5", page_icon="🤖")

# --- UI & LOGIC ---
with st.sidebar:
    sifre = st.text_input("🔑 Şifre:", type="password")
    
    if sifre == KURUCU_SIFRESI:
        mod = "Kurucu"
        isim = st.selectbox("👤 Kimsin Reis?", ["Ayaz Reis", "Mehmet Reis"])
    else:
        mod = "Misafir"
        isim = "Ziyaretçi"
        
    if st.button("🔄 Sohbeti Temizle"):
        st.session_state.messages = []
        st.rerun()

# Stil ve Tema
st.markdown(f"""
    <style>
    .assistant-box {{ background-color: rgba(30, 30, 30, 0.9); padding: 15px; border-radius: 10px; border-left: 5px solid gold; margin-bottom: 10px; }}
    .user-box {{ background-color: rgba(255, 255, 255, 0.1); padding: 15px; border-radius: 10px; margin-bottom: 10px; text-align: right; }}
    .aslan-header {{ display: flex; align-items: center; gap: 10px; font-weight: bold; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 5px; }}
    .user-header {{ display: flex; align-items: center; justify-content: flex-end; gap: 10px; font-weight: bold; margin-bottom: 8px; }}
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 Aslan Parçası V11.5")

if "messages" not in st.session_state: st.session_state.messages = []

# Mesajları yazdır
for m in st.session_state.messages:
    if m["role"] == "assistant":
        st.markdown(f"""
            <div class="assistant-box">
                <div class="aslan-header"><img src="{AVATAR_URL}" width="30" style="border-radius:50%"> Aslan Parçası</div>
                <div>{m['content']}</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="user-box">
                <div class="user-header">{isim} <img src="{USER_AVATAR}" width="30" style="border-radius:50%"></div>
                <div>{m['content']}</div>
            </div>
        """, unsafe_allow_html=True)

def ai_cevap(mesaj_gecmisi, mod, isim):
    headers = {"Authorization": f"Bearer {API_KEY}", "HTTP-Referer": "https://aslan-parcasi-widget.onrender.com", "X-Title": "Aslan Parcasi"}
    
    # Kimlik mantığı
    if isim == "Mehmet Reis":
        kimlik = "Sen Aslan Parçası'sın. Ayaz Reis'in yardımcısı olan Mehmet Reis'in yanındasın. Mehmet Reis'e sadık ve saygılı davran."
    elif isim == "Ayaz Reis":
        kimlik = "Sen Aslan Parçası'sın. Kurucun Ayaz Reis'in yanındasın."
    else:
        kimlik = "Sen Aslan Parçası'sın. Karşındaki kişiye düzgün ve nazik bir şekilde yardımcı ol."
        
    sistem = {"role": "system", "content": f"Kullanıcı: {isim}. {kimlik}"}
    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json={"model": MODEL, "messages": [sistem] + mesaj_gecmisi[-6:]})
        return res.json()['choices'][0]['message']['content']
    except Exception: return "Sistem meşgul, tekrar dene Reis."

# Giriş alanı
user_input = st.chat_input("Mesajını yaz...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    cevap = ai_cevap(st.session_state.messages, mod, isim)
    st.session_state.messages.append({"role": "assistant", "content": cevap})
    st.rerun()
