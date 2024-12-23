# pages/_Adicionar_Cashback.py

import streamlit as st
from data_manager import get_session, Customer, CashbackTransaction, CashbackStatus
from datetime import datetime, timedelta

def transacoes_page():
    st.title("➕ Adicionar Cashback")
    
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
        
        # Adicionar Cashback
        st.subheader(f"Adicionar Cashback para {customer.nome}")
        valor_compra = st.number_input("Valor da Compra (R$)", min_value=0.01, step=0.01, value=100.00)
        percentual_cashback = st.number_input("Percentual de Cashback (%)", min_value=0.0, max_value=100.0, step=0.1, value=10.0)
        
        # Calcular o valor do cashback
        valor_cashback = (valor_compra * percentual_cashback) / 100 if valor_compra > 0 else 0.0
        st.write(f"**Valor do Cashback Calculado:** R${valor_cashback:.2f}")
        
        validade = st.number_input("Validade do Cashback (dias)", min_value=1, value=30)
        
        if st.button("Adicionar Cashback"):
            if valor_cashback > 0 and validade > 0:
                expiration_date = datetime.utcnow() + timedelta(days=int(validade))
                transacao = CashbackTransaction(
                    customer_id=customer.customer_id,
                    valor=valor_cashback,
                    expiration_date=expiration_date,
                    status=CashbackStatus.active
                )
                session.add(transacao)
                session.commit()
                st.success(f"Cashback de R${valor_cashback:.2f} adicionado para {customer.nome}. Expira em {expiration_date.date()}.")
            else:
                st.warning("Valor do cashback e validade devem ser maiores que zero.")
    
    session.close()
