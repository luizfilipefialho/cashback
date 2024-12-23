# pages/2_Transacoes.py

import streamlit as st
from data_manager import get_session, Customer, CashbackTransaction, CashbackStatus
from datetime import datetime, timedelta

def transacoes_page():
    st.title("💰 Gestão de Transações de Cashback")
    
    session = get_session()
    
    # Selecionar Cliente
    clientes = session.query(Customer).all()
    if not clientes:
        st.info("Nenhum cliente cadastrado. Adicione um cliente primeiro.")
        session.close()
        return
    
    cliente_options = [f"{c.nome} - {c.cpf}" for c in clientes]
    cliente = st.selectbox("Selecione o Cliente", cliente_options)
    if cliente:
        customer_cpf = cliente.split(" - ")[1]
        customer = session.query(Customer).filter(Customer.cpf == customer_cpf).first()
        
        st.subheader(f"Adicionar Cashback para {customer.nome}")
        valor = st.number_input("Valor do Cashback (R$)", min_value=0.01, step=0.01)
        validade = st.number_input("Validade (dias)", min_value=1, value=30)
        
        if st.button("Adicionar Cashback"):
            if valor > 0 and validade > 0:
                expiration_date = datetime.utcnow() + timedelta(days=int(validade))
                transacao = CashbackTransaction(
                    customer_id=customer.customer_id,
                    valor=valor,
                    expiration_date=expiration_date,
                    status=CashbackStatus.active
                )
                session.add(transacao)
                session.commit()
                st.success(f"Cashback de R${valor:.2f} adicionado para {customer.nome}. Expira em {expiration_date.date()}.")
            else:
                st.warning("Valor e validade devem ser maiores que zero.")
    
    # Listar Transações Ativas
    st.subheader("Transações Ativas")
    transacoes = session.query(CashbackTransaction).filter(
        CashbackTransaction.status == CashbackStatus.active
    ).all()
    if transacoes:
        data = []
        for t in transacoes:
            data.append({
                "Cliente": t.customer.nome,
                "CPF": t.customer.cpf,
                "Valor": f"R${t.valor:.2f}",
                "Expira em": t.expiration_date.date()
            })
        st.table(data)
    else:
        st.info("Nenhuma transação ativa encontrada.")
    
    session.close()
