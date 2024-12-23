# pages/3_Expirados.py

import streamlit as st
from data_manager import get_session, CashbackExpired

def expirados_page():
    st.title("⏰ Cashback Expirados")
    
    session = get_session()
    
    # Query para expirados entre 1 e 30 dias
    expirados_1_30 = session.query(CashbackExpired).filter(
        CashbackExpired.days_after_expiration.between(1, 30)
    ).count()
    
    # Query para expirados acima de 30 dias
    expirados_31_plus = session.query(CashbackExpired).filter(
        CashbackExpired.days_after_expiration > 30
    ).count()
    
    # Query para total expirado
    total_expirado = session.query(CashbackExpired).count()
    
    st.metric("Expirados entre 1 e 30 dias", expirados_1_30)
    st.metric("Expirados acima de 30 dias", expirados_31_plus)
    st.metric("Total Expirado", total_expirado)
    
    st.subheader("Detalhes dos Cashback Expirados")
    expirados = session.query(CashbackExpired).all()
    if expirados:
        data = []
        for e in expirados:
            data.append({
                "Transação ID": e.transaction_id,
                "Cliente": e.transaction.customer.nome,
                "Valor": f"R${e.transaction.valor:.2f}",
                "Data de Expiração": e.transaction.expiration_date.date(),
                "Data de Expiração Registrada": e.expired_date.date(),
                "Dias Após Expiração": e.days_after_expiration
            })
        st.table(data)
    else:
        st.info("Nenhum cashback expirado encontrado.")
    
    session.close()
