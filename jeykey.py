import streamlit as st
import requests

# Configuración visual de la pestaña del navegador
st.set_page_config(page_title="Jey Key", page_icon="🤖", layout="centered")

# Tu clave de API oculta para el motor interno
API_KEY = "AQ.Ab8RN6LBOA6GZgOQjuZkPr9mru1oCbVqftjiaaeAg0bwSQDqTA"
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

# Título principal de la interfaz pública
st.title("🤖 Jey Key")
st.write("¡Bienvenida! Tu asistente virtual inteligente está listo. Todo tu historial se guardará aquí abajo.")
st.markdown("---")

# --- MEMORIA INTERNA DEL CHAT ---
if "historial" not in st.session_state:
    st.session_state.historial = []

# --- MOSTRAR LOS MENSAJES GUARDADOS ---
for mensaje in st.session_state.historial:
    if mensaje["rol"] == "usuario":
        with st.chat_message("user"):
            st.write(mensaje["texto"])
    else:
        with st.chat_message("assistant"):
            st.write(mensaje["texto"])

# --- CASILLA DE ENTRADA DE TEXTO ---
if pregunta := st.chat_input("Escribe tu mensaje aquí..."):
    
    # Mostrar pregunta en pantalla
    with st.chat_message("user"):
        st.write(pregunta)
    
    # Guardar en memoria
    st.session_state.historial.append({"rol": "usuario", "texto": pregunta})
    
    # Llamar al motor de la IA
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
            
            # Mostrar respuesta de Jey Key en la pantalla
            with st.chat_message("assistant"):
                st.write(texto_ia)
                
            # Guardar en memoria
            st.session_state.historial.append({"rol": "ia", "texto": texto_ia})
        else:
            st.error(f"Error de conexión ({response.status_code})")

# --- TEXTO DE ADVERTENCIA PERSONALIZADO ABAJO DEL TODO ---
st.markdown("<br><br>", unsafe_allow_html=True) # Espacio en blanco para empujarlo al fondo
st.caption("⚠️ Jey Key está en desarrollo y puede cometer errores.")