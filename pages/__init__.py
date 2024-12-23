# pages/__init__.py
import streamlit as st

from pages._Clientes import clientes_page
from pages._Transacoes import transacoes_page
from pages._Expirados import expirados_page
from pages._Utilizar_Saldo import utilizar_saldo_page
from pages._Relatorios import relatorios_page

def load_pages():
    st.sidebar.title("Navegação")
    page = st.sidebar.radio("Ir para", [
        "Gestão de Clientes",
        "Gestão de Transações",
        "Cashback Expirados",
        "Utilizar Saldo",
        "Relatórios"
    ])
    
    if page == "Gestão de Clientes":
        clientes_page()
    elif page == "Gestão de Transações":
        transacoes_page()
    elif page == "Cashback Expirados":
        expirados_page()
    elif page == "Utilizar Saldo":
        utilizar_saldo_page()
    elif page == "Relatórios":
        relatorios_page()
