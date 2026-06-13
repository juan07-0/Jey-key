import streamlit as st
import json
import os
import datetime
import requests

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Jey Key Hub", layout="wide")
ARCHIVO_BD = "base_datos_chats.json"
# PEGA TU CLAVE AQUÍ ABAJO, ENTRE LAS COMILLAS
API_KEY = "AQ.Ab8RN6LsuvS7cR4zuS93OaC35AGtQzNmvvEx2_E6pWG0ylQNYg"

def cargar_bd():
    if os.path.exists(ARCHIVO_BD):
        try:
            with open(ARCHIVO_BD, "r", encoding="utf-8") as f: return json.load(f)
        except: return {}
    return {}

def guardar_bd(datos):
    with open(ARCHIVO_BD, "w", encoding="utf-8") as f: json.dump(datos, f, indent=4)

if "user" not in st.session_state: st.session_state.user = st.query_params.get("user", None)
base_datos = cargar_bd()

if not st.session_state.user:
    st.title("🔐 Acceso Jey Key Hub")
    email = st.text_input("Correo electrónico:")
    if st.button("Entrar"):
        if email:
            st.session_state.user = email
            st.query_params["user"] = email
            if email not in base_datos: base_datos[email] = {}
            guardar_bd(base_datos)
            st.rerun()
    st.stop()

mis_chats = base_datos.get(st.session_state.user, {})
with st.sidebar:
    st.title("📁 Jey Key Hub")
    if st.button("➕ Nuevo Chat"):
        id_c = "CHAT_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        mis_chats[id_c] = {"titulo": "Nuevo Chat", "mensajes": []}
        guardar_bd(base_datos)
        st.session_state.chat = id_c
        st.rerun()
    for id_c, datos in mis_chats.items():
        if st.button(datos["titulo"], key=id_c):
            st.session_state.chat = id_c
            st.rerun()

if "chat" in st.session_state and st.session_state.chat in mis_chats:
    chat_act = mis_chats[st.session_state.chat]
    st.title(chat_act["titulo"])
    
    for m in chat_act["mensajes"]:
        with st.chat_message(m["rol"]):
            st.write(m["texto"])
    
    prompt = st.chat_input("Escribe tu consulta...")
    if prompt:
        chat_act["mensajes"].append({"rol": "user", "texto": prompt})
        
        # Llamada a Gemini
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
        try:
            res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
            if res.status_code == 200:
                txt = res.json()['candidates'][0]['content']['parts'][0]['text']
                chat_act["mensajes"].append({"rol": "assistant", "texto": txt})
            else:
                chat_act["mensajes"].append({"rol": "assistant", "texto": "Error de conexión (401). Verifica tu clave en Google Cloud."})
        except:
            chat_act["mensajes"].append({"rol": "assistant", "texto": "Error crítico."})
            
        chat_act["titulo"] = prompt[:15]
        guardar_bd(base_datos)
        st.rerun()