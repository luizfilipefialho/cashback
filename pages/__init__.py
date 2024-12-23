# pages/__init__.py
import streamlit as st

from pages._Clientes import clientes_page
from pages._Adicionar_Cashback import transacoes_page
from pages._Expirados import expirados_page
from pages._Utilizar_Saldo import utilizar_saldo_page
from pages._Relatorios import relatorios_page
from pages._Gestao_Transacoes import gestao_transacoes_page


def load_pages():
    st.sidebar.image("1708967842_logo.webp", use_container_width=True)  # Substitua "path/to/logo.png" pelo caminho do seu logo.
    page = st.sidebar.radio("Gestão de Cashback", [
        "Gestão de Clientes",
        "Adicionar Cashback",
        "Gestão de Transações",
        "Cashback Expirados",
        "Utilizar Saldo",
        "Relatórios"
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

    st.sidebar.button("Logout", on_click=lambda: logout())  # Adiciona o botão de logout

def logout():
    st.session_state["authenticated"] = False
    st.session_state["username"] = None
    st.rerun()

