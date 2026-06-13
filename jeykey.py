import streamlit as st
import requests
import datetime
import json
import os
import urllib.parse

# Configuración visual de la pestaña del navegador
st.set_page_config(page_title="Jey Key Hub", page_icon="🤖", layout="wide")

# ==============================================================================
# --- CONFIGURACIÓN DE APIS Y BASE DE DATOS ---
# ==============================================================================

# Tu clave de Gemini (Fija y protegida para el chat de texto)
GEMINI_API_KEY = "AQ.Ab8RN6LBOA6GZgOQjuZkPr9mru1oCbVqftjiaaeAg0bwSQDqTA"
url_gemini = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

ARCHIVO_BD_LOCAL = "base_datos_chats.json"

def cargar_base_datos():
    if os.path.exists(ARCHIVO_BD_LOCAL):
        try:
            with open(ARCHIVO_BD_LOCAL, "r", encoding="utf-8") as f:
                return json.load(f)
        except: 
            return {}
    return {}

def guardar_base_datos(datos):
    try:
        with open(ARCHIVO_BD_LOCAL, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=4)
    except:
        pass

# 🍌 MOTOR DE ARTE ULTRA-ESTABLE (NANO BANANA)
def generar_imagen_gratis(prompt_texto):
    prompt_seguro = urllib.parse.quote(prompt_texto)
    # Conexión directa a Nano Banana para saltarnos los bloqueos de pago 402
    url_banana = f"https://nano-banana.picoapps.xyz/api/generate?prompt={prompt_seguro}"
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    respuesta = requests.get(url_banana, headers=headers, timeout=25)
    
    if respuesta.status_code == 200:
        return respuesta.content
    else:
        raise Exception(f"El servidor de Nano Banana está saturado (Error {respuesta.status_code}). ¡Intenta darle Enter otra vez!")

# ==============================================================================
# --- MANEJO DE SESIÓN Y AUTO-LOGIN ---
# ==============================================================================
base_datos_global = cargar_base_datos()

if "usuario_actual" not in st.session_state:
    if "user" in st.query_params:
        st.session_state.usuario_actual = st.query_params["user"]
    else:
        st.session_state.usuario_actual = None

if "chat_seleccionado" not in st.session_state:
    st.session_state.chat_seleccionado = None

# ==============================================================================
# --- PANTALLA DE INICIO DE SESIÓN ---
# ==============================================================================
if st.session_state.usuario_actual is None:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.title("🔐 Acceso Jey Key Hub")
        st.write("Escribe tu correo para ingresar a tus chats guardados:")
        
        correo = st.text_input("Correo Electrónico:", placeholder="usuario@correo.com").strip().lower()
        
        if st.button("Iniciar Sesión", use_container_width=True):
            if correo:
                st.session_state.usuario_actual = correo
                st.query_params["user"] = correo
                if correo not in base_datos_global:
                    base_datos_global[correo] = {}
                    guardar_base_datos(base_datos_global)
                st.rerun()
            else:
                st.error("Por favor, introduce un correo válido.")
    st.stop()

# ==============================================================================
# --- INTERFAZ PRINCIPAL (BARRA LATERAL) ---
# ==============================================================================
correo_activo = st.session_state.usuario_actual
mis_chats = base_datos_global.get(correo_activo, {})

with st.sidebar:
    st.title("📁 Jey Key Hub")
    st.caption(f"Cuenta: {correo_activo}")
    
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.usuario_actual = None
        st.session_state.chat_seleccionado = None
        st.query_params.clear()
        st.rerun()
        
    st.markdown("---")
    
    if st.button("🎨 Generar Arte Gratis", use_container_width=True):
        id_chat = "ARTE_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        mis_chats[id_chat] = {"titulo": "🎨 Nuevo Arte", "tipo": "arte", "mensajes": []}
        base_datos_global[correo_activo] = mis_chats
        guardar_base_datos(base_datos_global)
        st.session_state.chat_seleccionado = id_chat
        st.rerun()

    if st.button("➕ Nuevo Chat (Texto)", use_container_width=True):
        id_chat = "CHAT_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        mis_chats[id_chat] = {"titulo": "💬 Nuevo Chat", "tipo": "chat", "mensajes": []}
        base_datos_global[correo_activo] = mis_chats
        guardar_base_datos(base_datos_global)
        st.session_state.chat_seleccionado = id_chat
        st.rerun()
        
    st.markdown("### Historial Sincronizado")
    for id_chat, datos_chat in sorted(list(mis_chats.items()), reverse=True):
        icon = "🎨" if datos_chat.get("tipo") == "arte" else "💬"
        if st.button(f"{icon} {datos_chat['titulo']}", key=id_chat, use_container_width=True):
            st.session_state.chat_seleccionado = id_chat
            st.rerun()

# ==============================================================================
# --- ZONA DE TRABAJO CENTRAL ---
# ==============================================================================
if st.session_state.chat_seleccionado and st.session_state.chat_seleccionado in mis_chats:
    chat_actual = mis_chats[st.session_state.chat_seleccionado]
    es_arte = chat_actual.get("tipo") == "arte"
    
    st.title(f"{'🎨 Estudio de Arte' if es_arte else '🤖 Chat Inteligente'}: {chat_actual['titulo']}")
    st.markdown("---")
    
    # Mostrar mensajes guardados en este chat
    for mensaje in chat_actual["mensajes"]:
        with st.chat_message("user" if mensaje["rol"] == "usuario" else "assistant"):
            if es_arte and "url_imagen" in mensaje:
                st.image(mensaje["url_imagen"], caption=mensaje["texto"])
            else:
                st.write(mensaje["texto"])

    # Entrada de texto única
    prompt = st.chat_input("Escribe aquí tu petición para Jey Key...")
    
    if prompt:
        with st.chat_message("user"):
            st.write(prompt)
        chat_actual["mensajes"].append({"rol": "usuario", "texto": prompt})
        guardar_base_datos(base_datos_global)
        
        cambiar_titulo = (chat_actual["titulo"] in ["🎨 Nuevo Arte", "💬 Nuevo Chat"])
        
        # --- MODO ESTUDIO DE ARTE ---
        if es_arte:
            with st.spinner("Pintando con Nano Banana... 🎨🍌"):
                try:
                    bytes_imagen = generar_imagen_gratis(prompt)
                    prompt_seguro = urllib.parse.quote(prompt)
                    url_final = f"https://nano-banana.picoapps.xyz/api/generate?prompt={prompt_seguro}"
                    
                    with st.chat_message("assistant"):
                        st.image(bytes_imagen, caption="¡Imagen lista!")
                    
                    chat_actual["mensajes"].append({
                        "rol": "ia", 
                        "texto": prompt, 
                        "url_imagen": url_final
                    })
                    if cambiar_titulo:
                        chat_actual["titulo"] = prompt[:20] + "..." if len(prompt) > 20 else prompt
                    
                    guardar_base_datos(base_datos_global)
                    st.rerun()
                except Exception as e:
                    st.error(f"{e}")
                    
        # --- MODO CHAT INTELIGENTE ---
        else:
            with st.spinner("Jey Key está pensando... 🧠"):
                payload_chat = {"contents": [{"parts": [{"text": prompt}]}]}
                try:
                    response = requests.post(url_gemini, json=payload_chat, timeout=15)
                    if response.status_code == 200:
                        data = response.json()
                        texto_ia = data['candidates'][0]['content']['parts'][0]['text']
                        
                        with st.chat_message("assistant"):
                            st.write(texto_ia)
                        chat_actual["mensajes"].append({"rol": "ia", "texto": texto_ia})
                        
                        if cambiar_titulo:
                            chat_actual["titulo"] = prompt[:20] + "..." if len(prompt) > 20 else prompt
                        
                        guardar_base_datos(base_datos_global)
                        st.rerun()
                    elif response.status_code == 429:
                        st.error("Gemini recibió muchas preguntas seguidas. Espera 5 segundos y presiona Enter de nuevo.")
                    else:
                        st.error(f"Error de conexión con Gemini (Código {response.status_code})")
                except Exception as e:
                    st.error("La conexión tardó demasiado. Vuelve a enviar el mensaje.")
else:
    st.title("🤖🎨 ¡Bienvenido a Jey Key Hub Pro!")
    st.write("Selecciona o crea un espacio en el menú izquierdo para empezar a trabajar.")