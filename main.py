# main.py

import streamlit as st
from data_manager import init_db, verificar_expirados
import pages

def main():
    # Inicializa o banco de dados e cria as tabelas se não existirem
    init_db()
    
    # Verifica e atualiza cashback expirado
    verificar_expirados()
    
    # Carrega as páginas
    pages.load_pages()

if __name__ == "__main__":
    main()
