# pages/__init__.py
import streamlit as st

from pages._Clientes import clientes_page
from pages._Adicionar_Cashback import transacoes_page
from pages._Expirados import expirados_page
from pages._Utilizar_Saldo import utilizar_saldo_page
from pages._Relatorios import relatorios_page
from pages._Gestao_Transacoes import gestao_transacoes_page
from pages._Importar_Transacoes import importar_transacoes_page


def load_pages():
    st.sidebar.image("1708967842_logo.webp", use_container_width=True)  # Substitua "path/to/logo.png" pelo caminho do seu logo.
    if "username" in st.session_state and st.session_state["username"]:
        user_name = st.session_state["username"].capitalize()
        st.sidebar.write(f"Olá, **{user_name}**!")
    page = st.sidebar.radio("Gestão de Cashback", [
        "Gestão de Clientes",
        "Utilizar Saldo",
        "Adicionar Cashback",
        "Gestão de Transações",
        "Cashback Expirados",
        "Relatórios",
        "Importação"
    ])
    

    
    if page == "Gestão de Clientes":
        clientes_page()
    elif page == "Adicionar Cashback":
        transacoes_page()
    elif page == "Gestão de Transações":
        gestao_transacoes_page()
    elif page == "Cashback Expirados":
        expirados_page()
    elif page == "Utilizar Saldo":
        utilizar_saldo_page()
    elif page == "Relatórios":
        relatorios_page()
    elif page == "Importação":
        importar_transacoes_page()

    st.sidebar.button("Logout", on_click=lambda: logout())  # Adiciona o botão de logout

def logout():
    st.session_state["authenticated"] = False
    st.session_state["username"] = None
    st.rerun()

