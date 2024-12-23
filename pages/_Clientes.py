# pages/1_Clientes.py

import streamlit as st
from data_manager import get_session, Customer
from sqlalchemy.exc import IntegrityError

def clientes_page():
    st.title("📇 Gestão de Clientes")
    
    menu = ["Adicionar Cliente", "Buscar Clientes"]
    choice = st.radio("Escolha uma opção", menu)
    
    session = get_session()
    
    if choice == "Adicionar Cliente":
        st.subheader("Adicionar Novo Cliente")
        nome = st.text_input("Nome")
        cpf = st.text_input("CPF")
        telefone = st.text_input("Telefone")
        
        if st.button("Salvar"):
            if nome and cpf and telefone:
                novo_cliente = Customer(nome=nome, cpf=cpf, telefone=telefone)
                try:
                    session.add(novo_cliente)
                    session.commit()
                    st.success(f"Cliente {nome} adicionado com sucesso!")
                except IntegrityError:
                    session.rollback()
                    st.error("CPF já cadastrado.")
            else:
                st.warning("Por favor, preencha todos os campos.")
    
    elif choice == "Buscar Clientes":
        st.subheader("Buscar Clientes")
        busca = st.text_input("Nome ou CPF")
        
        if st.button("Buscar"):
            if busca:
                resultados = session.query(Customer).filter(
                    (Customer.nome.ilike(f"%{busca}%")) | 
                    (Customer.cpf.ilike(f"%{busca}%"))
                ).all()
                if resultados:
                    for cliente in resultados:
                        st.write(f"**Nome:** {cliente.nome}")
                        st.write(f"**CPF:** {cliente.cpf}")
                        st.write(f"**Telefone:** {cliente.telefone}")
                        st.write("---")
                else:
                    st.info("Nenhum cliente encontrado.")
            else:
                st.warning("Insira um nome ou CPF para buscar.")
    
    session.close()
