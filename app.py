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
    if mod == "Kurucu":
        user_bg, assistant_bg = "rgba(10, 40, 10, 0.6)", "rgba(20, 20, 20, 0.8)"
        themes = {
            "Aslan İni": ("linear-gradient(to bottom, #1a1a00, #000000)", "white"),
            "Kraliyet": ("linear-gradient(to bottom, #2c0000, #000000)", "white"),
            "Teknoloji": ("linear-gradient(to bottom, #001a33, #000000)", "white"),
            "Orman Derinliği": ("linear-gradient(to bottom, #003300, #000000)", "white"),
            "Uzay": ("linear-gradient(to bottom, #1a0033, #000000)", "white")
        }
    else:
        user_bg, assistant_bg = "rgba(200, 230, 255, 0.2)", "rgba(144, 238, 144, 0.7)"
        themes = {"Gün Işığı": ("#f0f2f6", "black"), "Huzur": ("#e0f7fa", "black")}
    return user_bg, assistant_bg, themes

with st.sidebar:
    sifre = st.text_input("🔑 Şifre:", type="password")
    mod = "Kurucu" if sifre == KURUCU_SIFRESI else "Misafir"
    if st.button("🔄 Sohbeti Temizle"):
        st.session_state.messages = []
        st.rerun()
    user_bg, assistant_bg, theme_map = get_theme_data(mod)
    tema_secimi = st.selectbox("Arka Plan Seç:", list(theme_map.keys()))
    bg_color, text_color = theme_map[tema_secimi]

# --- STYLE & TEKNİK JS ---
st.markdown(f"""
    <style>
    .stApp {{ background: {bg_color}; color: {text_color} !important; }}
    .stChatMessage p, .stChatMessage div {{ color: {'black' if mod == "Misafir" else text_color} !important; font-weight: 500 !important; }}
    .stChatMessage[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {{ background-color: {user_bg} !important; }}
    .stChatMessage[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) {{ background-color: {assistant_bg} !important; border-left: 5px solid gold; }}
    .fixed-input-area {{ position: fixed; bottom: 0; left: 0; width: 100%; padding: 10px; background: {bg_color}; z-index: 999; }}
    .aslan-avatar-wrapper {{ cursor: pointer; }}
    </style>
    <script>
    document.addEventListener('click', function(e) {{
        if (e.target.closest('.aslan-avatar-wrapper')) {{
            let toast = document.createElement('div');
            toast.innerText = 'Aslan Parçası';
            toast.style.cssText = 'position:fixed; top:20%; left:50%; transform:translateX(-50%); background:gold; color:black; padding:15px 30px; border-radius:15px; z-index:999999; font-weight:bold; box-shadow:0px 4px 15px rgba(0,0,0,0.5); opacity:1; transition: opacity 1s ease-out;';
            document.body.appendChild(toast);
            setTimeout(() => {{ toast.style.opacity = '0'; }}, 2000);
            setTimeout(() => {{ toast.remove(); }}, 3000);
        }}
    }});
    </script>
    """, unsafe_allow_html=True)

st.title("🤖 Aslan Parçası V11.3")

if "messages" not in st.session_state: st.session_state.messages = []

# Mesajları yazdırırken avatarı kendi HTML wrapper'ımıza alıyoruz
for m in st.session_state.messages:
    if m["role"] == "assistant":
        with st.chat_message("assistant"):
            st.markdown(f'<div class="aslan-avatar-wrapper"><img src="{AVATAR_URL}" width="40" style="border-radius:50%"></div>', unsafe_allow_html=True)
            st.markdown(m["content"])
    else:
        st.chat_message("user").markdown(m["content"])

def ai_cevap(mesaj_gecmisi, mod):
    headers = {"Authorization": f"Bearer {API_KEY}", "HTTP-Referer": "https://aslan-parcasi-widget.onrender.com", "X-Title": "Aslan Parcasi"}
    kimlik = """Sen Aslan Parçası'sın. Kurucun Ayaz Reis. Sadece düzgün Türkçe konuş."""
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
    with st.chat_message("assistant"):
        st.markdown(f'<div class="aslan-avatar-wrapper"><img src="{AVATAR_URL}" width="40" style="border-radius:50%"></div>', unsafe_allow_html=True)
        cevap = ai_cevap(st.session_state.messages, mod)
        st.markdown(cevap)
    st.session_state.messages.append({"role": "assistant", "content": cevap})
    st.rerun()
