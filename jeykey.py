import streamlit as st
import requests
import datetime
import json
import os
import urllib.parse

st.set_page_config(page_title="Jey Key Hub", layout="wide")
ARCHIVO_BD = "base_datos_chats.json"

def cargar_bd():
    if os.path.exists(ARCHIVO_BD):
        try:
            with open(ARCHIVO_BD, "r", encoding="utf-8") as f: return json.load(f)
        except: return {}
    return {}

def guardar_bd(datos):
    with open(ARCHIVO_BD, "w", encoding="utf-8") as f: json.dump(datos, f)

if "user" not in st.session_state: st.session_state.user = st.query_params.get("user", None)
base_datos = cargar_bd()

if not st.session_state.user:
    st.title("🔐 Acceso Jey Key Hub")
    email = st.text_input("Ingresa tu correo:")
    if st.button("Entrar"):
        st.session_state.user = email
        st.query_params["user"] = email
        if email not in base_datos: base_datos[email] = {}
        guardar_bd(base_datos)
        st.rerun()
    st.stop()

mis_chats = base_datos.get(st.session_state.user, {})
with st.sidebar:
    st.title("📁 Jey Key Hub")
    if st.button("🎨 Nuevo Arte"):
        id_c = "ARTE_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        mis_chats[id_c] = {"titulo": "Nuevo Arte", "tipo": "arte", "msgs": []}
        guardar_bd(base_datos)
        st.session_state.chat = id_c
        st.rerun()
    if st.button("💬 Nuevo Chat"):
        id_c = "CHAT_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        mis_chats[id_c] = {"titulo": "Nuevo Chat", "tipo": "chat", "msgs": []}
        guardar_bd(base_datos)
        st.session_state.chat = id_c
        st.rerun()
    st.write("---")
    for id_c, datos in mis_chats.items():
        if st.button(datos["titulo"], key=id_c):
            st.session_state.chat = id_c
            st.rerun()

if "chat" in st.session_state and st.session_state.chat in mis_chats:
    chat_act = mis_chats[st.session_state.chat]
    st.title(chat_act["titulo"])
    
    for m in chat_act["msgs"]:
        with st.chat_message(m["rol"]):
            if m.get("tipo") == "img":
                st.image(m["url"])
            else:
                st.write(m.get("texto", ""))
    
    prompt = st.chat_input("Escribe algo...")
    if prompt:
        chat_act["msgs"].append({"rol": "user", "texto": prompt})
        if chat_act["tipo"] == "arte":
            # Usamos un parámetro 'seed' aleatorio para que el servidor siempre genere una imagen nueva
            # y la URL sea única, evitando errores de caché o bloqueo.
            url_img = f"https://image.pollinations.ai/p/{urllib.parse.quote(prompt)}?width=512&height=512&nologo=true&seed={datetime.datetime.now().microsecond}"
            
            # --- ESTA ES LA CLAVE PARA QUE SE MUESTRE ---
            # Usamos 'use_column_width=True' para que Streamlit se adapte al tamaño de tu contenedor
            chat_act["msgs"].append({"rol": "assistant", "tipo": "img", "url": url_img})
        else:
            try:
                payload = {"contents": [{"parts": [{"text": prompt}]}]}
                res = requests.post("https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=AQ.Ab8RN6LBOA6GZgOQjuZkPr9mru1oCbVqftjiaaeAg0bwSQDqTA", json=payload, timeout=10)
                if res.status_code == 200:
                    txt = res.json()['candidates'][0]['content']['parts'][0]['text']
                    chat_act["msgs"].append({"rol": "assistant", "texto": txt})
                else:
                    chat_act["msgs"].append({"rol": "assistant", "texto": "Error de conexión. Intenta de nuevo."})
            except:
                chat_act["msgs"].append({"rol": "assistant", "texto": "Error crítico."})
        
        chat_act["titulo"] = prompt[:15]
        guardar_bd(base_datos)
        st.rerun()