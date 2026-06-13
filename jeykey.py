import streamlit as st
import requests
import datetime
import json
import os
import time

# Configuración visual de la pestaña del navegador
st.set_page_config(page_title="Jey Key - Art Studio", page_icon="🎨", layout="wide")

# ==============================================================================
# --- CONFIGURACIÓN DE CLAVES SECRETAS (API KEYS) ---
# ==============================================================================

# 1. TU CLAVE DE GEMINI (LA QUE YA USABAS PARA CHATEAR)
GEMINI_API_KEY = "AQ.Ab8RN6LBOA6GZgOQjuZkPr9mru1oCbVqftjiaaeAg0bwSQDqTA"
url_gemini = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

# 2. TU NUEVA CLAVE DE OPENAI (PARA DALL-E/IMÁGENES)
# 👉 ¡Pega aquí tu nueva clave que empieza por sk-...!
OPENAI_API_KEY = "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" 
url_dalle = "https://api.openai.com/v1/images/generations"

# ==============================================================================
# --- FUNCIONES DE BASE DE DATOS (NO TOCAR) ---
# ==============================================================================
ARCHIVO_BD = "base_datos_chats.json"

def cargar_base_datos():
    if os.path.exists(ARCHIVO_BD):
        try:
            with open(ARCHIVO_BD, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return {}
    return {}

def guardar_base_datos(datos):
    with open(ARCHIVO_BD, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)

# ==============================================================================
# --- INICIALIZACIÓN DE SESIÓN Y DATOS ---
# ==============================================================================
if "usuario_actual" not in st.session_state:
    st.session_state.usuario_actual = None

if "chat_seleccionado" not in st.session_state:
    st.session_state.chat_seleccionado = None

base_datos_global = cargar_base_datos()

# ==============================================================================
# --- PANTALLA DE INICIO DE SESIÓN ---
# ==============================================================================
if st.session_state.usuario_actual is None:
    # Usamos columnas para centrar el formulario de registro
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🔐 Registro Jey Key")
        st.markdown("<h3 style='text-align: center; color: #4CAF50;'>¡Bienvenida, Danna!</h3>", unsafe_allow_html=True)
        st.write("Ingresa tu correo para acceder a tu historial permanente y a las funciones de arte.")
        
        correo = st.text_input("Correo Electrónico:", placeholder="ejemplo@correo.com").strip().lower()
        
        if st.button("Ingresar a Jey Key Hub", use_container_width=True):
            if correo:
                st.session_state.usuario_actual = correo
                if correo not in base_datos_global:
                    base_datos_global[correo] = {}
                    guardar_base_datos(base_datos_global)
                st.rerun()
            else:
                st.error("Debes escribir un correo válido.")
    
    # Detenemos la ejecución del resto del script si no hay sesión
    st.stop()

# ==============================================================================
# --- PANTALLA PRINCIPAL (LOGUEADO) ---
# ==============================================================================
correo_activo = st.session_state.usuario_actual
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
    
    # Nuevo botón dedicado a Crear Arte
    if st.button("🎨 Generar Arte", use_container_width=True):
        id_chat = "ARTE_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        mis_chats[id_chat] = {
            "titulo": "🎨 Nuevo Arte",
            "tipo": "arte",
            "mensajes": [] # Aquí guardaremos las imágenes generadas
        }
        base_datos_global[correo_activo] = mis_chats
        guardar_base_datos(base_datos_global)
        st.session_state.chat_seleccionado = id_chat
        st.rerun()

    if st.button("➕ Nuevo chat", use_container_width=True):
        id_chat = "CHAT_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        mis_chats[id_chat] = {
            "titulo": "💬 Nuevo Chat",
            "tipo": "chat",
            "mensajes": []
        }
        base_datos_global[correo_activo] = mis_chats
        guardar_base_datos(base_datos_global)
        st.session_state.chat_seleccionado = id_chat
        st.rerun()
        
    st.markdown("### Tus Chats")
    
    # Mostrar chats y arte en orden inverso (más nuevo arriba)
    for id_chat, datos_chat in sorted(list(mis_chats.items()), reverse=True):
        # Determinamos el ícono y el prefijo
        icon = "🎨" if datos_chat.get("tipo") == "arte" else "💬"
        prefix = "ARTE: " if datos_chat.get("tipo") == "arte" else ""
        
        button_label = f"{icon} {prefix}{datos_chat['titulo']}"
        if st.button(button_label, key=id_chat, use_container_width=True):
            st.session_state.chat_seleccionado = id_chat
            st.rerun()

# ==============================================================================
# --- ZONA CENTRAL: CHAT O GENERADOR DE ARTE SELECCIONADO ---
# ==============================================================================
if st.session_state.chat_seleccionado and st.session_state.chat_seleccionado in mis_chats:
    chat_actual = mis_chats[st.session_state.chat_seleccionado]
    es_arte = chat_actual.get("tipo") == "arte"
    
    # Cabecera dinámica
    if es_arte:
        st.title(f"🎨 Estudio de Arte: {chat_actual['titulo']}")
    else:
        st.title(f"🤖 Chat Inteligente: {chat_actual['titulo']}")
    st.markdown("---")
    
    # --- MOSTRAR EL HISTORIAL GUARDADO ---
    for mensaje in chat_actual["mensajes"]:
        if mensaje["rol"] == "usuario":
            with st.chat_message("user"):
                st.write(mensaje["texto"])
        elif mensaje["rol"] == "ia":
            with st.chat_message("assistant"):
                # Si es un chat de arte, mostramos la imagen. Si no, mostramos el texto.
                if es_arte and "url_imagen" in mensaje:
                    st.image(mensaje["url_imagen"], caption=f"Generado por DALL-E para: {chat_actual['titulo']}")
                else:
                    st.write(mensaje["texto"])

    # --- ENTRADA DE TEXTO (CHAT INPUT) ---
    prompt = st.chat_input("Dile a Jey Key qué hacer...")
    
    if prompt:
        # 1. Mostrar y guardar prompt del usuario
        with st.chat_message("user"):
            st.write(prompt)
        chat_actual["mensajes"].append({"rol": "usuario", "texto": prompt})
        
        # Guardado intermedio de la base de datos
        base_datos_global[correo_activo] = mis_chats
        guardar_base_datos(base_datos_global)
        
        # Determinar si actualizamos el título
        cambiar_titulo = (chat_actual["titulo"] in ["🎨 Nuevo Arte", "💬 Nuevo Chat"])
        
        # ======================================================================
        # 👉 FLUJO A: GENERAR ARTE (DALL-E) 
        # ======================================================================
        if es_arte:
            with st.spinner("Jey Key está pintando tu obra de arte... 🎨✍️"):
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {OPENAI_API_KEY}"
                }
                payload_arte = {
                    "model": "dall-e-3", # Usamos el modelo más nuevo y potente
                    "prompt": prompt,
                    "n": 1,
                    "size": "1024x1024"
                }
                
                try:
                    response = requests.post(url_dalle, headers=headers, json=payload_arte)
                    
                    if response.status_code == 200:
                        data = response.json()
                        url_imagen_ia = data['data'][0]['url']
                        
                        # Mostrar la imagen
                        with st.chat_message("assistant"):
                            st.image(url_imagen_ia, caption="¡Aquí tienes tu obra maestra!")
                        
                        # Guardar la URL en el historial (¡Ojo! Las URLs caducan en 1 hora, luego habrá que regenerar o descargar)
                        chat_actual["mensajes"].append({"rol": "ia", "texto": f"[Imagen Generada para: {prompt}]", "url_imagen": url_imagen_ia})
                        
                        # Actualizar título si es necesario
                        if cambiar_titulo:
                            chat_actual["titulo"] = prompt[:20] + "..." if len(prompt) > 20 else prompt
                        
                        # Guardado final de la base de datos
                        base_datos_global[correo_activo] = mis_chats
                        guardar_base_datos(base_datos_global)
                        
                        # Si cambió el título, refrescamos para que se vea en la barra lateral
                        if cambiar_titulo:
                            st.rerun()

                    elif response.status_code == 429:
                        st.error("⚠️ Error 429: Demasiadas solicitudes de arte. Espera un momento.")
                    elif response.status_code == 400:
                        st.error("⚠️ Error 400: Solicitud de arte incorrecta. Verifica tu prompt.")
                    else:
                        st.error(f"Error de conexión artística ({response.status_code}). Verifica tu Clave de OpenAI.")

                except Exception as e:
                    st.error(f"Ocurrió un error inesperado al generar arte: {e}")

        # ======================================================================
        # 👉 FLUJO B: CHAT NORMAL (GEMINI)
        # ======================================================================
        else:
            with st.spinner("Jey Key está pensando su respuesta... 🧠"):
                payload_chat = {
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }]
                }
                
                try:
                    response = requests.post(url_gemini, json=payload_chat)
                    
                    if response.status_code == 200:
                        data = response.json()
                        texto_ia = data['candidates'][0]['content']['parts'][0]['text']
                        
                        # Mostrar y guardar respuesta
                        with st.chat_message("assistant"):
                            st.write(texto_ia)
                        chat_actual["mensajes"].append({"rol": "ia", "texto": texto_ia})
                        
                        # Actualizar título si es necesario
                        if cambiar_titulo:
                            chat_actual["titulo"] = prompt[:25] + "..." if len(prompt) > 25 else prompt
                        
                        # Guardado final de la base de datos
                        base_datos_global[correo_activo] = mis_chats
                        guardar_base_datos(base_datos_global)
                        
                        # Si cambió el título, refrescamos
                        if cambiar_titulo:
                            st.rerun()
                    else:
                        st.error(f"Error de conexión de chat ({response.status_code})")
                
                except Exception as e:
                    st.error(f"Ocurrió un error inesperado al chatear: {e}")

else:
    # Pantalla de bienvenida principal
    st.title("🤖🎨 ¡Bienvenida a Jey Key Hub!")
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("<h3 style='color: #4CAF50;'>💬 Tu Chat Inteligente</h3>", unsafe_allow_html=True)
        st.write("Haz clic en **'➕ Nuevo chat'** a la izquierda para tener conversaciones profundas sobre cualquier tema con Gemini.")
    with col2:
        st.markdown("<h3 style='color: #E91E63;'>🎨 Tu Estudio de Arte</h3>", unsafe_allow_html=True)
        st.write("Haz clic en **'🎨 Generar Arte'** para dar vida a tus ideas visuales y crear imágenes increíbles con DALL-E 3.")
        
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.caption("⚠️ Jey Key Hub está en desarrollo. Las imágenes son generadas por DALL-E 3 y el chat por Gemini.")