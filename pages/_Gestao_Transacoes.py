# pages/_Gestao_Transacoes.py

import streamlit as st
from data_manager import get_session, CashbackTransaction, CashbackUsage, Customer, CashbackStatus
from datetime import datetime

def gestao_transacoes_page():
    st.title("📜 Gestão de Transações")
    
    session = get_session()
    
    # Obter todas as transações de cashback
    st.subheader("Transações de Adição de Saldo")
    transacoes_adicao = session.query(CashbackTransaction).all()
    if transacoes_adicao:
        data_adicao = []
        for t in transacoes_adicao:
            data_adicao.append({
                "Cliente": t.customer.nome,
                "CPF": t.customer.cpf,
                "Valor Adicionado (R$)": f"{t.valor:.2f}",
                "Data de Criação": t.created_at.strftime("%d/%m/%Y"),
                "Expiração": t.expiration_date.strftime("%d/%m/%Y"),
                "Status": t.status.value,
            })
        st.table(data_adicao)
    else:
        st.info("Nenhuma transação de adição de saldo encontrada.")
    
    # Obter todas as transações de utilização de saldo
    st.subheader("Transações de Utilização de Saldo")
    transacoes_utilizacao = session.query(CashbackUsage).all()
    if transacoes_utilizacao:
        data_utilizacao = []
        for t in transacoes_utilizacao:
            cliente = session.query(Customer).filter(Customer.customer_id == t.customer_id).first()
            data_utilizacao.append({
                "Cliente": cliente.nome,
                "CPF": cliente.cpf,
                "Valor Utilizado (R$)": f"{t.used_value:.2f}",
                "Data de Utilização": t.used_at.strftime("%d/%m/%Y")
            })
        st.table(data_utilizacao)
    else:
        st.info("Nenhuma transação de utilização de saldo encontrada.")
    
    session.close()
