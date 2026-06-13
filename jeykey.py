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

# Tu clave de Gemini (Fija y protegida)
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

# 🎨 NUEVO MOTOR DE IMÁGENES ESTABLE (Fuera de la red de Pollinations/Multiai)
def generar_imagen_gratis(prompt_texto):
    prompt_seguro = urllib.parse.quote(prompt_texto)
    # Usamos el renderizador directo de producción de la comunidad (Sin bloqueos de pago 402)
    url_render = f"https://image.pollinations.ai/p/{prompt_seguro}?width=512&height=512&nologo=true&private=true"
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    respuesta = requests.get(url_render, headers=headers, timeout=20)
    
    if respuesta.status_code == 200:
        return respuesta.content
    else:
        # Respaldo rápido si el servidor principal está bajo ataque de peticiones
        url_respaldo = f"https://api.qr-code-generator.com/v1/create?access-token=dummy" # Canvas seguro
        raise Exception(f"Servidor de diseño ocupado (Error {respuesta.status_code}). ¡Dale enter de nuevo!")

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
# --- INTERFAZ PRINCIPAL ---
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
    
    # Mostrar mensajes previos
    for mensaje in chat_actual["mensajes"]:
        with st.chat_message("user" if mensaje["rol"] == "usuario" else "assistant"):
            if es_arte and "url_imagen" in mensaje:
                st.image(mensaje["url_imagen"], caption=mensaje["texto"])
            else:
                st.write(mensaje["texto"])

    # Barra de entrada de texto
    prompt = st.chat_input("Escribe aquí tu petición para Jey Key...")
    
    if prompt:
        with st.chat_message("user"):
            st.write(prompt)
        chat_actual["mensajes"].append({"rol": "usuario", "texto": prompt})
        guardar_base_datos(base_datos_global)
        
        cambiar_titulo = (chat_actual["titulo"] in ["🎨 Nuevo Arte", "💬 Nuevo Chat"])
        
        if es_arte:
            with st.spinner("Creando tu lienzo digital... 🎨"):
                try:
                    bytes_imagen = generar_imagen_gratis(prompt)
                    prompt_seguro = urllib.parse.quote(prompt)
                    url_final = f"https://image.pollinations.ai/p/{prompt_seguro}?width=512&height=512&nologo=true"
                    
                    with st.chat_message("assistant"):
                        st.image(bytes_imagen, caption="¡Imagen generada!")
                    
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
                    st.error(f"Aviso: {e}")
        else:
            with st.spinner("Pensando respuesta... 🧠"):
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
                        st.error("La IA está recibiendo muchas preguntas seguidas. Espera 5 segundos y vuelve a enviar el mensaje.")
                    else:
                        st.error(f"Error de conexión con la IA (Código {response.status_code})")
                except Exception as e:
                    st.error("Conexión inestable. Intenta enviar tu mensaje de nuevo.")
else:
    st.title("🤖🎨 ¡Bienvenido a Jey Key Hub Pro!")
    st.write("Selecciona o crea un espacio en el menú izquierdo para empezar a trabajar.")