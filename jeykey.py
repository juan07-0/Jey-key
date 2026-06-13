import streamlit as st
import requests
import datetime
import json
import os
import urllib.parse

# Configuración visual de la pestaña del navegador
st.set_page_config(page_title="Jey Key - Art Studio", page_icon="🎨", layout="wide")

# ==============================================================================
# --- CONFIGURACIÓN DE MOTOR GRATUITO ---
# ==============================================================================

# 1. TU CLAVE DE GEMINI (LA QUE YA USABAS PARA CHATEAR)
GEMINI_API_KEY = "AQ.Ab8RN6LBOA6GZgOQjuZkPr9mru1oCbVqftjiaaeAg0bwSQDqTA"
url_gemini = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

# 2. MOTOR DE ARTE GRATUITO (No necesita clave API de OpenAI)
# Usaremos Pollinations AI que genera imágenes espectaculares mediante texto de forma libre
def generar_imagen_gratis(prompt_texto):
    # Traducimos el texto a un formato seguro para enlaces web (URL encoding)
    prompt_seguro = urllib.parse.quote(prompt_texto)
    # Usamos el modelo 'flux' que es uno de los mejores del mundo y es gratis aquí
    url_imagen = f"https://image.pollinations.ai/p/{prompt_seguro}?width=1024&height=1024&model=flux&seed={datetime.datetime.now().microsecond}"
    return url_imagen

# ==============================================================================
# --- FUNCIONES DE BASE DE DATOS ---
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
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🔐 Registro Jey Key")
        st.markdown("<h3 style='text-align: center; color: #4CAF50;'>¡Estudio de Arte Gratis!</h3>", unsafe_allow_html=True)
        st.write("Ingresa tu correo para acceder a tu interfaz personalizada de chat y dibujo sin costos.")
        
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
    
    if st.button("🎨 Generar Arte Gratis", use_container_width=True):
        id_chat = "ARTE_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        mis_chats[id_chat] = {
            "titulo": "🎨 Nuevo Arte",
            "tipo": "arte",
            "mensajes": []
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
    
    for id_chat, datos_chat in sorted(list(mis_chats.items()), reverse=True):
        icon = "🎨" if datos_chat.get("tipo") == "arte" else "💬"
        prefix = "ARTE: " if datos_chat.get("tipo") == "arte" else ""
        
        button_label = f"{icon} {prefix}{datos_chat['titulo']}"
        if st.button(button_label, key=id_chat, use_container_width=True):
            st.session_state.chat_seleccionado = id_chat
            st.rerun()

# ==============================================================================
# --- ZONA CENTRAL ---
# ==============================================================================
if st.session_state.chat_seleccionado and st.session_state.chat_seleccionado in mis_chats:
    chat_actual = mis_chats[st.session_state.chat_seleccionado]
    es_arte = chat_actual.get("tipo") == "arte"
    
    if es_arte:
        st.title(f"🎨 Estudio de Arte: {chat_actual['titulo']}")
    else:
        st.title(f"🤖 Chat Inteligente: {chat_actual['titulo']}")
    st.markdown("---")
    
    # --- MOSTRAR EL HISTORIAL ---
    for mensaje in chat_actual["mensajes"]:
        if mensaje["rol"] == "usuario":
            with st.chat_message("user"):
                st.write(mensaje["texto"])
        elif mensaje["rol"] == "ia":
            with st.chat_message("assistant"):
                if es_arte and "url_imagen" in mensaje:
                    st.image(mensaje["url_imagen"], caption=f"Arte: {mensaje['texto']}")
                else:
                    st.write(mensaje["texto"])

    # --- ENTRADA DE TEXTO ---
    prompt = st.chat_input("Dile a Jey Key qué hacer...")
    
    if prompt:
        with st.chat_message("user"):
            st.write(prompt)
        chat_actual["mensajes"].append({"rol": "usuario", "texto": prompt})
        
        base_datos_global[correo_activo] = mis_chats
        guardar_base_datos(base_datos_global)
        
        cambiar_titulo = (chat_actual["titulo"] in ["🎨 Nuevo Arte", "💬 Nuevo Chat"])
        
        # ======================================================================
        # 👉 FLUJO A: GENERAR ARTE GRATIS
        # ======================================================================
        if es_arte:
            with st.spinner("Jey Key está pintando tu obra de arte gratis... 🎨✍️"):
                try:
                    # Llamamos a nuestra función mágica gratuita
                    url_imagen_ia = generar_imagen_gratis(prompt)
                    
                    # Mostramos la imagen de una vez en pantalla
                    with st.chat_message("assistant"):
                        st.image(url_imagen_ia, caption="¡Aquí tienes tu dibujo!")
                    
                    # Guardamos en la base de datos
                    chat_actual["mensajes"].append({
                        "rol": "ia", 
                        "texto": prompt, 
                        "url_imagen": url_imagen_ia
                    })
                    
                    if cambiar_titulo:
                        chat_actual["titulo"] = prompt[:20] + "..." if len(prompt) > 20 else prompt
                    
                    base_datos_global[correo_activo] = mis_chats
                    guardar_base_datos(base_datos_global)
                    
                    if cambiar_titulo:
                        st.rerun()
                except Exception as e:
                    st.error(f"Error al generar la imagen: {e}")

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
                        
                        with st.chat_message("assistant"):
                            st.write(texto_ia)
                        chat_actual["mensajes"].append({"rol": "ia", "texto": texto_ia})
                        
                        if cambiar_titulo:
                            chat_actual["titulo"] = prompt[:25] + "..." if len(prompt) > 25 else prompt
                        
                        base_datos_global[correo_activo] = mis_chats
                        guardar_base_datos(base_datos_global)
                        
                        if cambiar_titulo:
                            st.rerun()
                    else:
                        st.error(f"Error en el chat ({response.status_code})")
                except Exception as e:
                    st.error(f"Error inesperado: {e}")

else:
    st.title("🤖🎨 ¡Bienvenida a Jey Key Hub!")
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("<h3 style='color: #4CAF50;'>💬 Tu Chat Inteligente</h3>", unsafe_allow_html=True)
        st.write("Haz clic en **'➕ Nuevo chat'** para conversar de forma ilimitada con Gemini.")
    with col2:
        st.markdown("<h3 style='color: #E91E63;'>🎨 Tu Estudio de Arte Gratis</h3>", unsafe_allow_html=True)
        st.write("Haz clic en **'🎨 Generar Arte Gratis'** para crear imágenes con inteligencia artificial ilimitada y sin pagar nada.")
        
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.caption("⚠️ Jey Key Hub está en desarrollo. Las imágenes son generadas de forma libre y gratuita.")