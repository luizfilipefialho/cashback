# pages/4_Utilizar_Saldo.py

import streamlit as st
from data_manager import get_session, Customer, CashbackTransaction, CashbackUsage, CashbackStatus
from datetime import datetime

def utilizar_saldo_page():
    st.title("💳 Utilizar Saldo de Cashback")
    
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
        
        # Calcular saldo total ativo
        transacoes = session.query(CashbackTransaction).filter(
            CashbackTransaction.customer_id == customer.customer_id,
            CashbackTransaction.status == CashbackStatus.active
        ).order_by(CashbackTransaction.expiration_date).all()
        
        saldo_total = sum(t.valor for t in transacoes)
        st.write(f"**Saldo Total Disponível:** R${saldo_total:.2f}")
        
        valor_utilizar = st.number_input("Valor a Utilizar (R$)", min_value=0.00, max_value=saldo_total, step=0.01, value=saldo_total)
        
        if st.button("Utilizar Saldo"):
            if 0 < valor_utilizar <= saldo_total:
                valor_restante = valor_utilizar
                for transacao in transacoes:
                    if transacao.valor <= valor_restante:
                        valor_restante -= transacao.valor
                        transacao.status = CashbackStatus.used
                        transacao.used_at = datetime.utcnow()
                        transacao.used_value = transacao.valor
                    else:
                        transacao.valor -= valor_restante
                        transacao.used_value = valor_restante
                        transacao.used_at = datetime.utcnow()
                        valor_restante = 0
                        break
                # Registrar no uso
                usage = CashbackUsage(
                    customer_id=customer.customer_id,
                    used_value=valor_utilizar
                )
                session.add(usage)
                session.commit()
                st.success(f"R${valor_utilizar:.2f} utilizados do saldo de cashback de {customer.nome}.")
            else:
                st.warning("Valor inválido para utilizar.")
    
    session.close()
