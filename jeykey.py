import streamlit as st
import requests

# Configuración visual de la página web
st.set_page_config(page_title="Mi Chatbot", page_icon="🤖", layout="centered")

# Tu clave de API funcional
API_KEY = "AQ.Ab8RN6LBOA6GZgOQjuZkPr9mru1oCbVqftjiaaeAg0bwSQDqTA"
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

st.title("🤖 Mi Chat Personal con Gemini")
st.write("¡Bienvenida! Todo lo que hables aquí se irá guardando en el historial.")
st.markdown("---")

# --- PASO 1: CREAR EL CAJÓN DE LA MEMORIA ---
# Si es la primera vez que abrimos la página, creamos una lista vacía para el historial
if "historial" not in st.session_state:
    st.session_state.historial = []

# --- PASO 2: MOSTRAR EL HISTORIAL EN LA PÁGINA ---
# Dibujamos en la pantalla todos los mensajes que llevamos guardados hasta ahora
for mensaje in st.session_state.historial:
    if mensaje["rol"] == "usuario":
        with st.chat_message("user"):
            st.write(mensaje["texto"])
    else:
        with st.chat_message("assistant"):
            st.write(mensaje["texto"])

# --- PASO 3: CASILLA PARA ESCRIBIR (Diseño de chat real) ---
# Usamos 'chat_input' en vez de 'text_input' para que quede abajo como en ChatGPT
if pregunta := st.chat_input("Escribe tu mensaje aquí..."):
    
    # 1. Mostramos el mensaje del usuario en la pantalla de una vez
    with st.chat_message("user"):
        st.write(pregunta)
    
    # 2. Guardamos la pregunta en la memoria interna
    st.session_state.historial.append({"rol": "usuario", "texto": pregunta})
    
    # 3. Llamamos a Gemini
    with st.spinner("Pensando... 🧠"):
        payload = {
            "contents": [{
                "parts": [{"text": pregunta}]
            }]
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            texto_ia = data['candidates'][0]['content']['parts'][0]['text']
            
            # 4. Mostramos la respuesta de la IA en la pantalla
            with st.chat_message("assistant"):
                st.write(texto_ia)
                
            # 5. Guardamos la respuesta de la IA en la memoria interna
            st.session_state.historial.append({"rol": "ia", "texto": texto_ia})
        else:
            st.error(f"Error de conexión ({response.status_code})")