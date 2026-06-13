import streamlit as st
import requests

# Configuración visual de la página web
st.set_page_config(page_title="Jey Key", page_icon="🤖", layout="centered")

# Tu clave de API que ya sabemos que funciona perfectamente
API_KEY = "AQ.Ab8RN6LBOA6GZgOQjuZkPr9mru1oCbVqftjiaaeAg0bwSQDqTA"
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

# --- INTERFAZ GRÁFICA DE LA PÁGINA ---
st.title("🤖 Jey Key")
st.write("¡Bienvenida! Escribe lo que quieras en la casilla de abajo y presiona el botón.")
st.markdown("---")

# Caja de texto para escribir en la web
pregunta = st.text_input("¿Qué le quieres preguntar a la IA?", placeholder="Ej: Escribe un poema corto...")

# Botón interactivo para enviar la pregunta
if st.button("Enviar pregunta ✨"):
    if pregunta.strip():
        with st.spinner("Pensando respuesta... 🧠"):
            payload = {
                "contents": [{
                    "parts": [{"text": pregunta}]
                }]
            }
            
            # Conexión directa por internet con el servidor
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                texto_ia = data['candidates'][0]['content']['parts'][0]['text']
                
                # Mostramos el resultado con un diseño web bonito
                st.success("¡Completado!")
                st.markdown("**Respuesta de Gemini:**")
                st.info(texto_ia)
            else:
                st.error(f"Error de conexión ({response.status_code})")
    else:
        st.warning("Por favor, escribe una pregunta primero.")