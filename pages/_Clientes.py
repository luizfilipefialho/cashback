import streamlit as st
from data_manager import get_session, Customer, CashbackTransaction, CashbackStatus
from datetime import datetime, timedelta

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
                cliente_existente = session.query(Customer).filter(Customer.cpf == cpf).first()
                if cliente_existente:
                    st.error(f"O CPF {cpf} já está cadastrado para o cliente {cliente_existente.nome}.")
                else:
                    novo_cliente = Customer(nome=nome, cpf=cpf, telefone=telefone)
                    session.add(novo_cliente)
                    session.commit()
                    st.success(f"Cliente {nome} adicionado com sucesso!")
            else:
                st.warning("Por favor, preencha todos os campos.")
    
    elif choice == "Buscar Clientes":
        st.subheader("Lista de Clientes")
        busca = st.text_input("Digite o Nome ou CPF para buscar")
        
        if busca:
            clientes = session.query(Customer).filter(
                (Customer.nome.ilike(f"%{busca}%")) | 
                (Customer.cpf.ilike(f"%{busca}%"))
            ).all()
        else:
            clientes = session.query(Customer).all()
        
        if clientes:
            data = []
            for cliente in clientes:
                saldo_total = sum(t.valor for t in cliente.transactions if t.status == CashbackStatus.active)
                saldo_expirando = sum(
                    t.valor for t in cliente.transactions 
                    if t.status == CashbackStatus.active and t.expiration_date <= datetime.utcnow() + timedelta(days=30)
                )
                data.append({
                    "Nome": cliente.nome,
                    "CPF": cliente.cpf,
                    "Telefone": cliente.telefone,
                    "Saldo Total (R$)": f"{saldo_total:.2f}",
                    "Saldo Expirando em 30 Dias (R$)": f"{saldo_expirando:.2f}"
                })
            st.table(data)
        else:
            st.info("Nenhum cliente encontrado com os critérios de busca.")
    
    session.close()
