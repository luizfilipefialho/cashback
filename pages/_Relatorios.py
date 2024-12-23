# pages/5_Relatorios.py

import streamlit as st
import pandas as pd
from data_manager import get_session, CashbackTransaction, CashbackExpired, CashbackUsage, Customer

def relatorios_page():
    st.title("📊 Relatórios e Exportações")
    
    session = get_session()
    
    menu = ["Exportar Clientes", "Exportar Transações", "Exportar Expirados", "Exportar Utilizações"]
    choice = st.selectbox("Escolha o Relatório", menu)
    
    if choice == "Exportar Clientes":
        clientes = session.query(Customer).all()
        data = [{
            "Nome": c.nome,
            "CPF": c.cpf,
            "Telefone": c.telefone,
            "Data de Cadastro": c.created_at.date()
        } for c in clientes]
        df = pd.DataFrame(data)
        st.dataframe(df)
        st.download_button(
            label="Baixar CSV",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name='clientes.csv',
            mime='text/csv'
        )
    
    elif choice == "Exportar Transações":
        transacoes = session.query(CashbackTransaction).all()
        data = [{
            "ID Transação": t.transaction_id,
            "ID Compra": t.id_compra,  # Adicionado
            "Cliente": t.customer.nome,
            "Valor": f"R${t.valor:.2f}",
            "Data de Criação": t.created_at.date(),
            "Criado Por": t.created_by,
            "Data de Expiração": t.expiration_date.date(),
            "Status": t.status.value
            } for t in transacoes]

        df = pd.DataFrame(data)
        st.dataframe(df)
        st.download_button(
            label="Baixar CSV",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name='transacoes.csv',
            mime='text/csv'
        )
    
    elif choice == "Exportar Expirados":
        expirados = session.query(CashbackExpired).all()
        data = [{
            "ID Expirado": e.expired_id,
            "Transação ID": e.transaction_id,
            "Cliente": e.transaction.customer.nome,
            "Valor": f"R${e.transaction.valor:.2f}",
            "Data de Expiração": e.transaction.expiration_date.date(),
            "Data de Expiração Registrada": e.expired_date.date(),
            "Dias Após Expiração": e.days_after_expiration
        } for e in expirados]
        df = pd.DataFrame(data)
        st.dataframe(df)
        st.download_button(
            label="Baixar CSV",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name='expirados.csv',
            mime='text/csv'
        )
    
    elif choice == "Exportar Utilizações":
        utilizacoes = session.query(CashbackUsage).all()
        data = [{
                "ID Uso": u.usage_id,
                "ID Compra": u.id_compra,  # Adicionado
                "Cliente": u.customer.nome,
                "Valor Utilizado": f"R${u.used_value:.2f}",
                "Data de Utilização": u.used_at.date(),
                "Utilizado Por": u.used_by
            } for u in utilizacoes]
        df = pd.DataFrame(data)
        st.dataframe(df)
        st.download_button(
            label="Baixar CSV",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name='utilizacoes.csv',
            mime='text/csv'
        )
    
    session.close()
