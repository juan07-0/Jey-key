import streamlit as st
import json
import os
import requests

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Jey Key Hub", layout="wide")
ARCHIVO_BD = "base_datos_chats.json"

# --- PEGA TU CLAVE AQUÍ ---
API_KEY = "AQ.Ab8RN6LsuvS7cR4zuS93OaC35AGtQzNmvvEx2_E6pWG0ylQNYg"

# --- FUNCIONES DE BASE DE DATOS ---
def cargar_bd():
    if os.path.exists(ARCHIVO_BD):
        try:
            with open(ARCHIVO_BD, "r", encoding="utf-8") as f: return json.load(f)
        except: return {}
    return {}

def guardar_bd(datos):
    with open(ARCHIVO_BD, "w", encoding="utf-8") as f: json.dump(datos, f, indent=4)

# --- ACCESO ---
if "user" not in st.session_state: st.session_state.user = st.query_params.get("user", None)
base_datos = cargar_bd()

if not st.session_state.user:
    st.title("🔐 Acceso Jey Key Hub")
    email = st.text_input("Correo electrónico:")
    if st.button("Entrar"):
        if email:
            st.session_state.user = email
            st.query_params["user"] = email
            guardar_bd(base_datos)
            st.rerun()
    st.stop()

# --- CHAT ---
st.title("🤖 Chat con Gemini")
prompt = st.chat_input("Escribe tu consulta...")

if prompt:
    # URL oficial de la API de Gemini
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    try:
        res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
        
        if res.status_code == 200:
            respuesta_json = res.json()
            texto_ia = respuesta_json['candidates'][0]['content']['parts'][0]['text']
            st.write(texto_ia)
        else:
            st.error(f"Error de conexión: {res.status_code}. Revisa tu clave.")
    except Exception as e:
        st.error("Error al conectar con la API.")