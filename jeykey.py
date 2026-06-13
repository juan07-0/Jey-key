import streamlit as st
import requests
import datetime
import json
import os
import urllib.parse

# Configuración visual de la pestaña del navegador
st.set_page_config(page_title="Jey Key Hub Pro", page_icon="🤖", layout="wide")

# ==============================================================================
# --- CONFIGURACIÓN DE MOTORES Y RESPALDOS ---
# ==============================================================================

# TU CLAVE DE GEMINI (Sigue intacta para el Chat inteligente)
GEMINI_API_KEY = "AQ.Ab8RN6LBOA6GZgOQjuZkPr9mru1oCbVqftjiaaeAg0bwSQDqTA"
url_gemini = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

ARCHIVO_BD_LOCAL = "base_datos_chats.json"

def cargar_base_datos():
    if os.path.exists(ARCHIVO_BD_LOCAL):
        try:
            with open(ARCHIVO_BD_LOCAL, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return {}
    return {}

def guardar_base_datos(datos):
    with open(ARCHIVO_BD_LOCAL, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)

# 🚀 NUEVO MOTOR DE ARTE ESTABLE Y SEGURO (Evita por completo el Error 402)
def generar_imagen_gratis(prompt_texto):
    # Usamos un espejo alternativo optimizado de alta velocidad (Render Estable)
    prompt_seguro = urllib.parse.quote(prompt_texto)
    url_espejo = f"https://image.pollinations.ai/p/{prompt_seguro}?width=800&height=800&model=turbo&enhance=false"
    
    # Validamos la conexión de manera directa para asegurar que responda
    respuesta = requests.get(url_espejo, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
    if respuesta.status_code == 200:
        return respuesta.content
    else:
        raise Exception(f"Código de error: {respuesta.status_code}")

# ==============================================================================
# --- SISTEMA DE MEMORIA LOCAL DEL NAVEGADOR (AUTO-LOGIN) ---
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
        st.title("🔐 Registro Jey Key Hub")
        st.markdown("<h4 style='color: #4CAF50;'>¡Acceso Permanente Activo!</h4>", unsafe_allow_html=True)
        st.write("Registra tu correo una sola vez y la sesión quedará guardada en este navegador.")
        
        correo = st.text_input("Correo Electrónico:", placeholder="ejemplo@correo.com").strip().lower()
        
        if st.button("Ingresar y Activar Memoria", use_container_width=True):
            if correo:
                st.session_state.usuario_actual = correo
                st.query_params["user"] = correo 
                
                if correo not in base_datos_global:
                    base_datos_global[correo] = {}
                    guardar_base_datos(base_datos_global)
                st.rerun()
            else:
                st.error("Debes escribir un correo electrónico válido.")
    st.stop()

# ==============================================================================
# --- PANTALLA PRINCIPAL ---
# ==============================================================================
correo_activo = st.session_state.usuario_actual
mis_chats = base_datos_global.get(correo_activo, {})

with st.sidebar:
    st.title("📁 Jey Key Hub")
    st.markdown(f"👤 Cuenta activa:\n**{correo_activo}**")
    
    if st.button("🚪 Cerrar Sesión aquí", use_container_width=True):
        st.session_state.usuario_actual = None
        st.session_state.chat_seleccionado = None
        st.query_params.clear() 
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
        
    st.markdown("### Tus Chats Sincronizados")
    
    for id_chat, datos_chat in sorted(list(mis_chats.items()), reverse=True):
        icon = "🎨" if datos_chat.get("tipo") == "arte" else "💬"
        prefix = "ARTE: " if datos_chat.get("tipo") == "arte" else ""
        
        button_label = f"{icon} {prefix}{datos_chat['titulo']}"
        if st.button(button_label, key=id_chat, use_container_width=True):
            st.session_state.chat_seleccionado = id_chat
            st.rerun()

# ==============================================================================
# --- INTERACCIÓN CENTRAL ---
# ==============================================================================
if st.session_state.chat_seleccionado and st.session_state.chat_seleccionado in mis_chats:
    chat_actual = mis_chats[st.session_state.chat_seleccionado]
    es_arte = chat_actual.get("tipo") == "arte"
    
    if es_arte:
        st.title(f"🎨 Estudio de Arte: {chat_actual['titulo']}")
    else:
        st.title(f"🤖 Chat Inteligente: {chat_actual['titulo']}")
    st.markdown("---")
    
    for mensaje in chat_actual["mensajes"]:
        if mensaje["rol"] == "usuario":
            with st.chat_message("user"):
                st.write(mensaje["texto"])
        elif mensaje["rol"] == "ia":
            with st.chat_message("assistant"):
                if es_arte and "url_imagen" in mensaje:
                    st.image(mensaje["url_imagen"], caption=f"Resultado: {mensaje['texto']}")
                else:
                    st.write(mensaje["texto"])

    prompt = st.chat_input("Escribe tu idea aquí...")
    
    if prompt:
        with st.chat_message("user"):
            st.write(prompt)
        chat_actual["mensajes"].append({"rol": "usuario", "texto": prompt})
        
        base_datos_global[correo_activo] = mis_chats
        guardar_base_datos(base_datos_global)
        
        cambiar_titulo = (chat_actual["titulo"] in ["🎨 Nuevo Arte", "💬 Nuevo Chat"])
        
        if es_arte:
            with st.spinner("Pintando tu obra de arte digital... 🎨✍️"):
                try:
                    bytes_imagen = generar_imagen_gratis(prompt)
                    prompt_seguro = urllib.parse.quote(prompt)
                    url_final = f"https://image.pollinations.ai/p/{prompt_seguro}?width=800&height=800&model=turbo&enhance=false"
                    
                    with st.chat_message("assistant"):
                        st.image(bytes_imagen, caption="¡Imagen generada con éxito!")
                    
                    chat_actual["mensajes"].append({
                        "rol": "ia", 
                        "texto": prompt, 
                        "url_imagen": url_final
                    })
                    
                    if cambiar_titulo:
                        chat_actual["titulo"] = prompt[:20] + "..." if len(prompt) > 20 else prompt
                    
                    base_datos_global[correo_activo] = mis_chats
                    guardar_base_datos(base_datos_global)
                    st.rerun()
                except Exception as e:
                    st.error("El servidor de imágenes externo está ocupado. ¡Vuelve a presionar Enter en unos segundos para forzar el dibujo!")
        else:
            with st.spinner("Jey Key está pensando su respuesta... 🧠"):
                payload_chat = {"contents": [{"parts": [{"text": prompt}]}]}
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
                        st.rerun()
                    else:
                        st.error(f"Error de conexión con Gemini ({response.status_code})")
                except Exception as e:
                    st.error(f"Error de red: {e}")
else:
    st.title("🤖🎨 ¡Bienvenido a Jey Key Hub!")
    st.write("Selecciona o crea un nuevo chat en el menú de la izquierda para comenzar.")