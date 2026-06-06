import streamlit as st
from google import genai

# Anahtar kodun içinde yazmaz, Streamlit arka planından güvenle çekilir.
# Bu yüzden anahtarın kara listeye girmez.
API_KEY = st.secrets["GOOGLE_API_KEY"]

st.title("🤖 ASLAN PARÇASI V8.9")

if prompt := st.chat_input("Reis bir şey de..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        try:
            # Client'ı doğrudan gizli anahtarla başlatıyoruz
            client = genai.Client(api_key=API_KEY)
            
            # Modeli çağırıyoruz
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt
            )
            
            st.markdown(response.text)
        except Exception as e:
            st.error(f"Sistem Hatası: {e}")
