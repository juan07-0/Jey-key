import streamlit as st
import datetime
import json
import os
import urllib.parse

# Configuración básica
st.set_page_config(page_title="Jey Key Hub", layout="wide")
ARCHIVO_BD = "base_datos_chats.json"

# Funciones de base de datos simples
def cargar_bd():
    if os.path.exists(ARCHIVO_BD):
        try:
            with open(ARCHIVO_BD, "r", encoding="utf-8") as f: return json.load(f)
        except: return {}
    return {}

def guardar_bd(datos):
    with open(ARCHIVO_BD, "w", encoding="utf-8") as f: json.dump(datos, f)

# Inicio de sesión simple
if "user" not in st.session_state: st.session_state.user = st.query_params.get("user", None)
base_datos = cargar_bd()

if not st.session_state.user:
    st.title("🔐 Acceso")
    email = st.text_input("Correo:")
    if st.button("Entrar"):
        st.session_state.user = email
        st.query_params["user"] = email
        if email not in base_datos: base_datos[email] = {}
        guardar_bd(base_datos)
        st.rerun()
    st.stop()

# Interfaz
mis_chats = base_datos.get(st.session_state.user, {})
with st.sidebar:
    if st.button("🎨 Nuevo Arte"):
        id_c = "ARTE_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        mis_chats[id_c] = {"titulo": "Nuevo Arte", "tipo": "arte", "msgs": []}
        guardar_bd(base_datos)
        st.session_state.chat = id_c
        st.rerun()
    
    st.write("---")
    for id_c, datos in mis_chats.items():
        if st.button(datos["titulo"], key=id_c):
            st.session_state.chat = id_c
            st.rerun()

# Lógica de Chat y Arte
if "chat" in st.session_state and st.session_state.chat in mis_chats:
    chat_act = mis_chats[st.session_state.chat]
    st.title(chat_act["titulo"])
    
    # Mostrar historial
    for m in chat_act["msgs"]:
        with st.chat_message(m["rol"]):
            if m.get("tipo") == "img":
                st.image(m["url"], use_column_width=True)
            else:
                st.write(m["texto"])
    
    # Entrada de usuario
    prompt = st.chat_input("Dile a Jey Key qué hacer...")
    if prompt:
        chat_act["msgs"].append({"rol": "user", "texto": prompt})
        
        if chat_act["tipo"] == "arte":
            # URL de Pollinations directa: es lo más estable que existe hoy
            url_img = f"https://image.pollinations.ai/p/{urllib.parse.quote(prompt)}?width=512&height=512&nologo=true&seed={datetime.datetime.now().microsecond}"
            chat_act["msgs"].append({"rol": "assistant", "tipo": "img", "url": url_img})
            chat_act["titulo"] = prompt[:15]
        else:
            chat_act["msgs"].append({"rol": "assistant", "texto": "Modo texto activo (Gemini desconectado para evitar errores)."})
            
        guardar_bd(base_datos)
        st.rerun()