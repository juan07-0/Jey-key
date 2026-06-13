import streamlit as st
import requests

# Configuración visual de la pestaña del navegador
st.set_page_config(page_title="Jey Key", page_icon="🤖", layout="centered")

# Tu clave de API oculta para el motor interno
API_KEY = "AQ.Ab8RN6LBOA6GZgOQjuZkPr9mru1oCbVqftjiaaeAg0bwSQDqTA"
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

# --- INICIALIZAR LA BASE DE DATOS LOCAL ---
# Creamos un "cajón" para guardar los historiales de cada correo diferente
if "base_datos_usuarios" not in st.session_state:
    st.session_state.base_datos_usuarios = {}

if "usuario_actual" not in st.session_state:
    st.session_state.usuario_actual = None

# --- PANTALLA DE REGISTRO / LOGIN ---
if st.session_state.usuario_actual is None:
    st.title("🔐 Registro de Usuario - Jey Key")
    st.write("Por favor, ingresa tu correo electrónico para acceder a tu historial personalizado.")
    
    correo = st.text_input("Correo Electrónico:", placeholder="ejemplo@correo.com").strip().lower()
    
    if st.button("Ingresar al Chat"):
        if correo:
            # Guardamos cuál es el usuario que está navegando ahora
            st.session_state.usuario_actual = correo
            
            # Si es un correo nuevo que nunca había entrado, le creamos su historial vacío
            if correo not in st.session_state.base_datos_usuarios:
                st.session_state.base_datos_usuarios[correo] = []
                
            st.rerun() # Reiniciamos la página para mostrar el chat
        else:
            st.error("Debes escribir un correo válido para continuar.")

# --- PANTALLA DEL CHAT (Solo se muestra si ya puso el correo) ---
else:
    correo_activo = st.session_state.usuario_actual
    
    # Botón arriba a la derecha para cerrar sesión
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title("🤖 Jey Key")
    with col2:
        if st.button("Cerrar Sesión"):
            st.session_state.usuario_actual = None
            st.rerun()
            
    st.write(f"👤 Sesión activa: **{correo_activo}**")
    st.markdown("---")

    # Obtener el historial específico de ESTE usuario
    historial_usuario = st.session_state.base_datos_usuarios[correo_activo]

    # --- MOSTRAR LOS MENSAJES GUARDADOS DE ESTE CORREO ---
    for mensaje in historial_usuario:
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
        
        # Guardar en el historial del usuario activo
        historial_usuario.append({"rol": "usuario", "texto": pregunta})
        
        # Llamar al motor de la IA
        with st.spinner("Jey Key está pensando... 🧠"):
            payload = {
                "contents": [{
                    "parts": [{"text": pregunta}]
                }]
            }
            
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                texto_ia = data['candidates'][0]['content']['parts'][0]['text']
                
                # Mostrar respuesta de Jey Key
                with st.chat_message("assistant"):
                    st.write(texto_ia)
                    
                # Guardar la respuesta en el historial del usuario activo
                historial_usuario.append({"rol": "ia", "texto": texto_ia})
            else:
                st.error(f"Error de conexión ({response.status_code})")

    # --- TEXTO DE ADVERTENCIA ABAJO DEL TODO ---
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.caption("⚠️ Jey Key está en desarrollo y puede cometer errores.")