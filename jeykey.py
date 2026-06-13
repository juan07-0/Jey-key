import streamlit as st
import requests
import urllib.parse

# Configuración visual de la pestaña del navegador
st.set_page_config(page_title="Jey Key Hub", page_icon="🤖", layout="wide")

# ==============================================================================
# --- CONFIGURACIÓN DE APIS ---
# ==============================================================================

# Tu clave de Gemini para el chat de texto
GEMINI_API_KEY = "AQ.Ab8RN6LBOA6GZgOQjuZkPr9mru1oCbVqftjiaaeAg0bwSQDqTA"
url_gemini = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

# ==============================================================================
# --- INTERFAZ Y MEMORIA DE CHATS ---
# ==============================================================================

# Inicializamos el historial en la memoria de la sesión si no existe
if "historial_chats" not in st.session_state:
    st.session_state.historial_chats = []

if "tipo_servicio" not in st.session_state:
    st.session_state.tipo_servicio = "💬 Chat Inteligente"

# --- BARRA LATERAL ---
with st.sidebar:
    st.title("📁 Jey Key Hub")
    st.markdown("---")
    
    # Selector de modo de trabajo
    st.session_state.tipo_servicio = st.radio(
        "¿Qué deseas hacer hoy?",
        ["💬 Chat Inteligente", "🎨 Estudio de Arte (Gratis)"]
    )
    
    st.markdown("---")
    if st.button("🗑️ Limpiar Pantalla / Nuevo Chat", use_container_width=True):
        st.session_state.historial_chats = []
        st.rerun()

# ==============================================================================
# --- ZONA DE TRABAJO CENTRAL ---
# ==============================================================================
st.title(f"{st.session_state.tipo_servicio}")
st.write("Desarrollado con amor para que nunca se caiga. ✨")
st.markdown("---")

# Mostrar los mensajes que ya se han enviado en esta sesión
for mensaje in st.session_state.historial_chats:
    with st.chat_message(mensaje["rol"]):
        if mensaje["tipo"] == "imagen":
            st.image(mensaje["contenido"], caption="Lienzo generado por Jey Key")
        else:
            st.write(mensaje["contenido"])

# Cuadro de entrada de texto abajo
prompt = st.chat_input("Escribe aquí tu petición o idea...")

if prompt:
    # 1. Mostrar el mensaje del usuario inmediatamente
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.historial_chats.append({"rol": "user", "tipo": "texto", "contenido": prompt})
    
    # 2. PROCESAR SEGÚN EL MODO SELECCIONADO
    if st.session_state.tipo_servicio == "🎨 Estudio de Arte (Gratis)":
        with st.spinner("Dibujando tu idea con el motor de arte... 🎨"):
            try:
                # Convertimos el texto a un formato seguro para la web
                prompt_seguro = urllib.parse.quote(prompt)
                # Generamos un enlace directo. ¡Este método no se cae porque la carga la hace el navegador!
                url_imagen_indestructible = f"https://image.pollinations.ai/p/{prompt_seguro}?width=512&height=512&nologo=true"
                
                with st.chat_message("assistant"):
                    st.image(url_imagen_indestructible, caption="¡Imagen lista!")
                
                st.session_state.historial_chats.append({
                    "rol": "assistant",
                    "tipo": "imagen",
                    "contenido": url_imagen_indestructible
                })
            except Exception as e:
                st.error("Hubo un problema al procesar el lienzo. Inténtalo de nuevo.")
                
    else:
        # MODO CHAT INTELIGENTE DE TEXTO
        with st.spinner("Jey Key está pensando la respuesta... 🧠"):
            payload_chat = {"contents": [{"parts": [{"text": prompt}]}]}
            try:
                response = requests.post(url_gemini, json=payload_chat, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    texto_ia = data['candidates'][0]['content']['parts'][0]['text']
                    
                    with st.chat_message("assistant"):
                        st.write(texto_ia)
                    
                    st.session_state.historial_chats.append({
                        "rol": "assistant",
                        "tipo": "texto",
                        "contenido": texto_ia
                    })
                elif response.status_code == 429:
                    st.error("El servidor de texto está saturado. Espera 5 segundos y vuelve a presionar Enter.")
                else:
                    st.error(f"Error de conexión con la IA (Código {response.status_code})")
            except Exception as e:
                st.error("La respuesta tardó demasiado en llegar. Intenta enviar el mensaje otra vez.")