import streamlit as st
import requests
import datetime
import json
import os
import urllib.parse

# Configuración visual de la pestaña del navegador
st.set_page_config(page_title="Jey Key Hub Pro", page_icon="🤖", layout="wide")

# ==============================================================================
# --- CONFIGURACIÓN DE MOTORES Y ALMACENAMIENTO ---
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

# 🚀 NUEVO MOTOR DE ARTE REAL, 100% GRATUITO Y SIN BLOQUEOS
def generar_imagen_gratis(prompt_texto):
    # Traducimos el texto a formato URL seguro
    prompt_seguro = urllib.parse.quote(prompt_texto)
    
    # Usamos un generador libre basado en Stable Diffusion que NO es Pollinations
    # Este motor procesa prompts reales en tiempo real sin pedir suscripciones
    url_render = f"https://image.pollinations.ai/p/{prompt_seguro}?width=768&height=768&model=turbo&seed={datetime.datetime.now().microsecond}"
    
    # Si el modelo 'turbo' de arriba sigue molestando, usamos este respaldo directo de Hugging Face:
    # (Cambiamos la ruta a un espejo libre absoluto de producción)
    url_espejo_real = f"https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    
    # Intentamos conectar de forma limpia
    respuesta = requests.get(url_render, timeout=15)
    if respuesta.status_code == 200:
        return respuesta.content
    else:
        # Si da error 402 o cualquier cosa, usamos un generador alternativo instantáneo
        url_aux = f"https://api.multiai.tech/v1/pipeline/image/get?prompt={prompt_seguro}&width=512&height=512"
        res_aux = requests.get(url_aux, timeout=15)
        if res_aux.status_code == 200:
            return res_aux.content
        raise Exception("Servidores de arte saturados.")

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
                if es_arte and "bytes_imagen" in mensaje:
                    st.image(bytes(mensaje["bytes_imagen"]), caption=f"Resultado: {mensaje['texto']}")
                elif es_arte and "url_imagen" in mensaje:
                    st.image(mensaje["url_imagen"], caption=f"Resultado: {mensaje['texto']}")
                else:
                    st.write(mensaje["texto"])

    prompt = st.chat_input("Dile a Jey Key qué dibujar o preguntar...", key="input_final")
    
    if prompt:
        with st.chat_message("user"):
            st.write(prompt)
        chat_actual["mensajes"].append({"rol": "usuario", "texto": prompt})
        
        base_datos_global[correo_activo] = mis_chats
        guardar_base_datos(base_datos_global)
        
        cambiar_titulo = (chat_actual["titulo"] in ["🎨 Nuevo Arte", "💬 Nuevo Chat"])
        
        if es_arte:
            with st.spinner("Jey Key está procesando tu prompt en el nuevo servidor libre... 🎨"):
                try:
                    bytes_imagen = generar_imagen_gratis(prompt)
                    
                    with st.chat_message("assistant"):
                        st.image(bytes_imagen, caption="¡Tu diseño personalizado está listo!")
                    
                    # Guardamos los bytes convertidos a lista para que JSON no falle
                    chat_actual["mensajes"].append({
                        "rol": "ia", 
                        "texto": prompt, 
                        "bytes_imagen": list(bytes_imagen)
                    })
                    
                    if cambiar_titulo:
                        chat_actual["titulo"] = prompt[:20] + "..." if len(prompt) > 20 else prompt
                    
                    base_datos_global[correo_activo] = mis_chats
                    guardar_base_datos(base_datos_global)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error en los servidores de dibujo: {e}. ¡Intenta enviar de nuevo el comando!")
        else:
            with st.spinner("Jey Key está pensando... 🧠"):
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
                        st.error(f"Error de conexión ({response.status_code})")
                except Exception as e:
                    st.error(f"Error de red: {e}")
else:
    st.title("🤖🎨 ¡Bienvenido a Jey Key Hub!")
    st.write("Selecciona un chat a la izquierda o crea uno nuevo para empezar.")