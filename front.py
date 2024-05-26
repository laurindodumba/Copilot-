import streamlit as st
from chat import handle_chat
from ai import config_page
import sqlite3
import pandas as pd
import os
import base64
import PyPDF2

def get_connection():
    return sqlite3.connect("files.db")

def create_files_table():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                data TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro ao criar a tabela 'files': {e}")

def insert_file(title, data):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO files (title, data) VALUES (?, ?)", (title, data))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"An error occurred: {e}")

def delete_file(title):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM files WHERE title = ?", (title,))
    conn.commit()
    conn.close()

def file_exists(title):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM files WHERE title = ?", (title,))
    exists = cursor.fetchone()[0] > 0
    conn.close()
    return exists

def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

if "history" not in st.session_state:
    st.session_state["history"] = []

def inject_bootstrap():
    bootstrap_link = """
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
    """
    st.markdown(bootstrap_link, unsafe_allow_html=True)

def create_footer():
    footer_html = """
        <div class="footer">
        <hr style="border-top: 1px solid #bbb;">
        <p style="text-align: center; font-size: 14px;">© 2024 DocSpyder </p>
        </div>
        """
    st.markdown(footer_html, unsafe_allow_html=True)

def get_image_base64(path):
    with open(path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

create_files_table()

inject_bootstrap()
page = st.sidebar.selectbox("Navegação", ["HOME", "CONFIGURAÇÃO"])

if page == "HOME":
    st.markdown("<h1 style='text-align: center;'>SOLUÇÃO AI GENERATIVA</h1>", unsafe_allow_html=True)
    image_path = os.path.join("foto", "Capturar.PNG")
    st.image(image_path, caption="Logo", use_column_width=True)
    image_base64 = get_image_base64(image_path)
    image_html = f"""
    <style>
    img {{
        border-radius: 15px;
    }}
    </style>
    <img src="data:image/png;base64,{image_base64}" width="1000">
    """
    st.markdown(image_html, unsafe_allow_html=True)

    if "input_text" not in st.session_state:
        st.session_state["input_text"] = ""

    user_input = st.text_input("Faça uma pergunta:", value=st.session_state["input_text"], key="user_input")
    send_button = st.button("Enviar")

    if send_button:
        response = handle_chat(user_input)
        st.session_state["history"].append(("Você", user_input))
        st.session_state["history"].append(("AI", response))
        st.session_state["input_text"] = ""

    for idx, (user, message) in enumerate(reversed(st.session_state["history"])):
        st.text_area(f"{user}: {idx}", value=message, key=f"msg{idx}{user[0]}", disabled=True)

elif page == "CONFIGURAÇÃO":
    config_page()
    create_footer()

uploaded_files = st.sidebar.file_uploader("Carregar arquivos", accept_multiple_files=True, type=['pdf'])
for uploaded_file in uploaded_files:
    if uploaded_file is not None:
        if not file_exists(uploaded_file.name):
            pdf_text = extract_text_from_pdf(uploaded_file)
            insert_file(uploaded_file.name, pdf_text)
            st.sidebar.success(f"Arquivo {uploaded_file.name} carregado com sucesso!")
        else:
            st.sidebar.warning(f"Arquivo {uploaded_file.name} já existe!")

conn = get_connection()
df = pd.read_sql_query("SELECT title FROM files", conn)
conn.close()

if not df.empty:
    st.sidebar.write("Arquivos Carregados")
    for idx, title in enumerate(df['title']):
        st.sidebar.text(title)
        if st.sidebar.button(f"Deletar {title}", key=f"delete_{idx}"):
            delete_file(title)
            st.sidebar.success(f"{title} deletado!")
            st.experimental_rerun()
