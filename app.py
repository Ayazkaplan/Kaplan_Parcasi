import streamlit as st
import requests
import os

# Ayarlar
API_KEY = os.environ.get("API_KEY")
MODEL = "anthropic/claude-3-haiku"
KURUCU_SIFRESI = "KAPLAN_REIS_74"
AVATAR_URL = "https://i.imgur.com/3EfO8Ae.jpeg"

st.set_page_config(page_title="Aslan Parçası V11.3", page_icon="🤖")

# --- UI LOGIC ---
def get_theme_data(mod):
    # Kutu arka plan renklerini belirledik
    assistant_box_bg = "rgba(144, 238, 144, 0.3)" if mod == "Misafir" else "rgba(30, 30, 30, 0.9)"
    
    if mod == "Kurucu":
        user_bg = "rgba(10, 40, 10, 0.6)"
        themes = {
            "Aslan İni": ("linear-gradient(to bottom, #1a1a00, #000000)", "white"),
            "Kraliyet": ("linear-gradient(to bottom, #2c0000, #000000)", "white"),
            "Teknoloji": ("linear-gradient(to bottom, #001a33, #000000)", "white")
        }
    else:
        user_bg = "rgba(200, 230, 255, 0.2)"
        themes = {"Gün Işığı": ("#f0f2f6", "black"), "Huzur": ("#e0f7fa", "black")}
    return user_bg, assistant_box_bg, themes

with st.sidebar:
    sifre = st.text_input("🔑 Şifre:", type="password")
    mod = "Kurucu" if sifre == KURUCU_SIFRESI else "Misafir"
    if st.button("🔄 Sohbeti Temizle"):
        st.session_state.messages = []
        st.rerun()
    user_bg, assistant_box_bg, theme_map = get_theme_data(mod)
    tema_secimi = st.selectbox("Arka Plan Seç:", list(theme_map.keys()))
    bg_color, text_color = theme_map[tema_secimi]

# --- STYLE ---
st.markdown(f"""
    <style>
    .stApp {{ background: {bg_color}; color: {text_color} !important; }}
    /* Asistan mesaj kutusu stili */
    .assistant-box {{ 
        background-color: {assistant_box_bg}; 
        padding: 15px; 
        border-radius: 10px; 
        border-left: 5px solid gold; 
        margin-bottom: 10px;
    }}
    .aslan-header {{ display: flex; align-items: center; gap: 10px; font-weight: bold; margin-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 5px; }}
    .fixed-input-area {{ position: fixed; bottom: 0; left: 0; width: 100%; padding: 10px; background: {bg_color}; z-index: 999; }}
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 Aslan Parçası V11.3")

if "messages" not in st.session_state: st.session_state.messages = []

# Mesajları yazdırırken kutu yapısını kullandık
for m in st.session_state.messages:
    if m["role"] == "assistant":
        st.markdown(f"""
            <div class="assistant-box">
                <div class="aslan-header">
                    <img src="{AVATAR_URL}" width="30" style="border-radius:50%"> Aslan Parçası
                </div>
                <div>{m['content']}</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.chat_message("user").markdown(m["content"])

def ai_cevap(mesaj_gecmisi, mod):
    headers = {"Authorization": f"Bearer {API_KEY}", "HTTP-Referer": "https://aslan-parcasi-widget.onrender.com", "X-Title": "Aslan Parcasi"}
    kimlik = "Sen Aslan Parçası'sın. Sadece düzgün Türkçe konuş."
    sistem = {"role": "system", "content": f"Mod: {mod}. {kimlik}"}
    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json={"model": MODEL, "messages": [sistem] + mesaj_gecmisi[-6:]})
        return res.json()['choices'][0]['message']['content']
    except Exception: return "Sistem meşgul, tekrar dene Reis."

st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown('<div class="fixed-input-area">', unsafe_allow_html=True)
with st.form(key='chat_form', clear_on_submit=True):
    user_input = st.text_input("", placeholder="Mesajını yaz...")
    submit_button = st.form_submit_button(label='Gönder')
st.markdown('</div>', unsafe_allow_html=True)

if submit_button and user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"): st.markdown(user_input)
    cevap = ai_cevap(st.session_state.messages, mod)
    st.session_state.messages.append({"role": "assistant", "content": cevap})
    st.rerun()
