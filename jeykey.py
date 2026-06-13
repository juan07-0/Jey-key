import streamlit as st
import requests
import datetime

# Configuración visual de la pestaña del navegador
st.set_page_config(page_title="Jey Key", page_icon="🤖", layout="wide")

# Tu clave de API oculta para el motor interno
API_KEY = "AQ.Ab8RN6LBOA6GZgOQjuZkPr9mru1oCbVqftjiaaeAg0bwSQDqTA"
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

# --- INICIALIZAR LA BASE DE DATOS LOCAL ---
if "base_datos_usuarios" not in st.session_state:
    st.session_state.base_datos_usuarios = {}

if "usuario_actual" not in st.session_state:
    st.session_state.usuario_actual = None

# Variable para saber qué chat tiene seleccionado el usuario en la barra lateral
if "chat_seleccionado" not in st.session_state:
    st.session_state.chat_seleccionado = None

# --- PANTALLA DE REGISTRO / LOGIN ---
if st.session_state.usuario_actual is None:
    st.title("🔐 Registro de Usuario - Jey Key")
    st.write("Por favor, ingresa tu correo electrónico para acceder a tu historial personalizado.")
    
    correo = st.text_input("Correo Electrónico:", placeholder="ejemplo@correo.com").strip().lower()
    
    if st.button("Ingresar al Chat"):
        if correo:
            st.session_state.usuario_actual = correo
            # Si el usuario es nuevo, le creamos un diccionario vacío para sus chats
            if correo not in st.session_state.base_datos_usuarios:
                st.session_state.base_datos_usuarios[correo] = {}
            st.rerun()
        else:
            st.error("Debes escribir un correo válido para continuar.")

# --- PANTALLA PRINCIPAL (CON BARRA LATERAL) ---
else:
    correo_activo = st.session_state.usuario_actual
    
    # Todos los chats que le pertenecen a este correo
    mis_chats = st.session_state.base_datos_usuarios[correo_activo]

    # --- CONFIGURACIÓN DE LA BARRA LATERAL (IZQUIERDA) ---
    with st.sidebar:
        st.title("📁 Jey Key Hub")
        st.write("👤 ¡Sesión Iniciada!") # Cambiado para mantener el correo oculto aquí también
        
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.usuario_actual = None
            st.session_state.chat_seleccionado = None
            st.rerun()
            
        st.markdown("---")
        
        # Botón para crear un nuevo chat
        if st.button("➕ Nuevo chat", use_container_width=True):
            id_chat = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            mis_chats[id_chat] = {
                "titulo": "Nuevo Chat",
                "mensajes": []
            }
            st.session_state.chat_seleccionado = id_chat
            st.rerun()
            
        st.markdown("### Tus Chats")
        
        # Mostrar la lista de todos los chats creados al lado izquierdo
        if not mis_chats:
            st.info("No tienes chats activos. ¡Crea uno nuevo arriba!")
        else:
            for id_chat, datos_chat in list(mis_chats.items()):
                if st.button(f"💬 {datos_chat['titulo']}", key=id_chat, use_container_width=True):
                    st.session_state.chat_seleccionado = id_chat
                    st.rerun()

    # --- ZONA CENTRAL: CONTENIDO DEL CHAT SELECCIONADO ---
    if st.session_state.chat_seleccionado and st.session_state.chat_seleccionado in mis_chats:
        chat_actual = mis_chats[st.session_state.chat_seleccionado]
        
        st.title(f"🤖 {chat_actual['titulo']}")
        st.markdown("---") # El correo que aparecía aquí ya fue borrado
        
        # Mostrar los mensajes del chat seleccionado
        for mensaje in chat_actual["mensajes"]:
            if mensaje["rol"] == "usuario":
                with st.chat_message("user"):
                    st.write(mensaje["texto"])
            else:
                with st.chat_message("assistant"):
                    st.write(mensaje["texto"])
                    
        # Casilla para escribir abajo
        if pregunta := st.chat_input("Escribe tu mensaje aquí..."):
            with st.chat_message("user"):
                st.write(pregunta)
                
            chat_actual["mensajes"].append({"rol": "usuario", "texto": pregunta})
            
            if chat_actual["titulo"] == "Nuevo Chat":
                chat_actual["titulo"] = pregunta[:25] + "..." if len(pregunta) > 25 else pregunta
                st.rerun()
                
            # Llamar al motor de IA
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
                    
                    with st.chat_message("assistant"):
                        st.write(texto_ia)
                        
                    chat_actual["mensajes"].append({"rol": "ia", "texto": texto_ia})
                else:
                    st.error(f"Error de conexión ({response.status_code})")
    else:
        # Pantalla de bienvenida
        st.title("🤖 ¡Bienvenida a Jey Key!")
        st.write("Selecciona un chat de la barra lateral izquierda o crea uno nuevo para empezar a conversar.")

    # --- ADVERTENCIA FIJA ABAJO ---
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.caption("⚠️ Jey Key está en desarrollo y puede cometer errores.")