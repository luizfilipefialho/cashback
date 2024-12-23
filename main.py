import streamlit as st
from data_manager import init_db, verificar_expirados
import pages

# Configuração inicial
st.set_page_config(page_title="Cashback Peregrino")

# Inicializa as variáveis de sessão no início
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "username" not in st.session_state:
    st.session_state["username"] = None

# Função para autenticação
def authenticate(username, password):
    if username in st.secrets["users"]:
        stored_password = st.secrets["users"][username]
        return password == stored_password
    return False

# Inicializa o banco de dados e verifica expirados
init_db()
verificar_expirados()

# Verifica o estado de autenticação
if not st.session_state["authenticated"]:
    # Página de Login
    st.title("Login")

    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")

    if st.button("Login"):
        if authenticate(username, password):
            st.success(f"Bem-vindo, {username}!")
            st.session_state["authenticated"] = True
            st.session_state["username"] = username  # Salva o nome do usuário logado
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos.")
else:
    # Página principal após autenticação
    pages.load_pages()
    
# Função de logout
