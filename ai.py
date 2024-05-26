import streamlit as st
import json
import os

CONFIG_PATH = "api_config.json"

def save_api_settings(api_key, default_user, model_option):
    config = {
        "api_key": api_key,
        "default_user": default_user,
        "model_option": model_option
    }
    with open(CONFIG_PATH, 'w') as config_file:
        json.dump(config, config_file)

def load_api_settings():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as config_file:
            config = json.load(config_file)
        return config
    return None

def config_page():
    st.title("CONFIGURAÇÃO")
    st.write("Parâmetros de configuração da API")
    
    config = load_api_settings()
    api_key = config['api_key'] if config else ""
    default_user = config['default_user'] if config else ""
    model_option = config['model_option'] if config else "gpt-3.5-turbo"

    with st.form("api_config"):
        api_key = st.text_input("Chave da API", value=api_key, type="password", help="Insira sua chave da API da OpenAI.")
        default_user = st.text_input("Usuário Padrão", value=default_user, help="Insira o identificador do usuário padrão.")
        model_option = st.selectbox("Modelo Padrão", ['gpt-3.5-turbo', 'text-embedding-ada-002', 'text-davinci-003'], index=['gpt-3.5-turbo', 'text-embedding-ada-002', 'text-davinci-003', 'gpt-4', 'gpt-4o'].index(model_option), help="Selecione o modelo de IA padrão para operações.")
        
        submit_button = st.form_submit_button("Salvar Configurações")
        
        if submit_button:
            save_api_settings(api_key, default_user, model_option)
            st.success("Configurações salvas com sucesso!")
