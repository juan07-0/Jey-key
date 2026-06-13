import streamlit as st
import requests
import datetime
import json
import os

# Configuración visual de la pestaña del navegador
st.set_page_config(page_title="Jey Key", page_icon="🤖", layout="wide")

# Tu clave de API oculta para el motor interno
API_KEY = "AQ.Ab8RN6LBOA6GZgOQjuZkPr9mru1oCbVqftjiaaeAg0bwSQDqTA"
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

# Nombre del archivo físico donde guardaremos los datos para siempre
ARCHIVO_BD = "base_datos_chats.json"

# --- FUNCIONES PARA GUARDAR Y LEER DEL DISCO ---
def cargar_base_datos():
    """Lee el archivo JSON guardado en el servidor. Si no existe, crea uno vacío."""
    if os.path.exists(ARCHIVO_BD):
        try:
            with open(ARCHIVO_BD, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def guardar_base_datos(datos):
    """Guarda físicamente todos los chats en el archivo JSON."""
    with open(ARCHIVO_BD, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)

# --- INICIALIZAR LA MEMORIA DE LA SESIÓN ACTUAL ---
if "usuario_actual" not in st.session_state:
    st.session_state.usuario_actual = None

if "chat_seleccionado" not in st.session_state:
    st.session_state.chat_seleccionado = None

# Cargamos los datos permanentes de inmediato
base_datos_global = cargar_base_datos()

# --- PANTALLA DE REGISTRO / LOGIN ---
if st.session_state.usuario_actual is None:
    st.title("🔐 Registro de Usuario - Jey Key")
    st.write("Por favor, ingresa tu correo electrónico para acceder a tu historial permanente.")
    
    correo = st.text_input("Correo Electrónico:", placeholder="ejemplo@correo.com").strip().lower()
    
    if st.button("Ingresar al Chat"):
        if correo:
            st.session_state.usuario_actual = correo
            # Si el correo nunca había existido en el archivo, le preparamos su espacio
            if correo not in base_datos_global:
                base_datos_global[correo] = {}
                guardar_base_datos(base_datos_global)
            st.rerun()
        else:
            st.error("Debes escribir un correo válido para continuar.")

# --- PANTALLA PRINCIPAL DEL CHAT ---
else:
    correo_activo = st.session_state.usuario_actual
    
    # Extraemos solo los chats de ESTE correo desde el archivo permanente
    mis_chats = base_datos_global.get(correo_activo, {})

    # --- BARRA LATERAL (IZQUIERDA) ---
    with st.sidebar:
        st.title("📁 Jey Key Hub")
        st.write("👤 ¡Sesión Iniciada!")
        
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.usuario_actual = None
            st.session_state.chat_seleccionado = None
            st.rerun()
            
        st.markdown("---")
        
        if st.button("➕ Nuevo chat", use_container_width=True):
            id_chat = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            mis_chats[id_chat] = {
                "titulo": "Nuevo Chat",
                "mensajes": []
            }
            # Guardamos la estructura del nuevo chat en el archivo fijo
            base_datos_global[correo_activo] = mis_chats
            guardar_base_datos(base_datos_global)
            
            st.session_state.chat_seleccionado = id_chat
            st.rerun()
            
        st.markdown("### Tus Chats")
        
        if not mis_chats:
            st.info("No tienes chats activos. ¡Crea uno nuevo arriba!")
        else:
            for id_chat, datos_chat in list(mis_chats.items()):
                if st.button(f"💬 {datos_chat['titulo']}", key=id_chat, use_container_width=True):
                    st.session_state.chat_seleccionado = id_chat
                    st.rerun()

    # --- ZONA CENTRAL: CHAT SELECCIONADO ---
    if st.session_state.chat_seleccionado and st.session_state.chat_seleccionado in mis_chats:
        chat_actual = mis_chats[st.session_state.chat_seleccionado]
        
        st.title(f"🤖 {chat_actual['titulo']}")
        st.markdown("---")
        
        # Mostrar el historial guardado en el archivo
        for mensaje in chat_actual["mensajes"]:
            if mensaje["rol"] == "usuario":
                with st.chat_message("user"):
                    st.write(mensaje["texto"])
            else:
                with st.chat_message("assistant"):
                    st.write(mensaje["texto"])
                    
        # Casilla de entrada de texto
        if pregunta := st.chat_input("Escribe tu mensaje aquí..."):
            with st.chat_message("user"):
                st.write(pregunta)
            
            # Insertar pregunta en los datos locales
            chat_actual["mensajes"].append({"rol": "usuario", "texto": pregunta})
            cambiar_titulo = (chat_actual["titulo"] == "Nuevo Chat")
                
            # Llamar a Jey Key
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
                    
                    # Insertar respuesta en los datos locales
                    chat_actual["mensajes"].append({"rol": "ia", "texto": texto_ia})
                    
                    # Si correspondía, cambiar el título
                    if cambiar_titulo:
                        chat_actual["titulo"] = pregunta[:25] + "..." if len(pregunta) > 25 else pregunta
                    
                    # --- EL TRUCO MAESTRO: Guardamos todo de forma permanente en el archivo .json ---
                    base_datos_global[correo_activo] = mis_chats
                    guardar_base_datos(base_datos_global)
                    
                    # Si cambió el título, refrescamos la pantalla
                    if cambiar_titulo:
                        st.rerun()
                else:
                    st.error(f"Error de conexión ({response.status_code})")
    else:
        st.title("🤖 ¡Bienvenida a Jey Key!")
        st.write("Selecciona un chat de la barra lateral izquierda o crea uno nuevo para empezar a conversar.")

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.caption("⚠️ Jey Key está en desarrollo y puede cometer errores.")