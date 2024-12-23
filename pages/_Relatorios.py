import streamlit as st
import pandas as pd
from data_manager import CashbackStatus, get_session, CashbackTransaction, CashbackExpired, CashbackUsage, Customer
from datetime import datetime

def relatorios_page():
    st.title("📊 Relatórios e Exportações")
    
    session = get_session()
    
    menu = ["Exportar Clientes", "Exportar Transações", "Exportar Expirados", "Exportar Utilizações", "Exportar Expiração de Saldos"]
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
            "ID Compra": t.id_compra,
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
            "ID Compra": u.id_compra,
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
    
    if choice == "Exportar Expiração de Saldos":
        agora = datetime.utcnow()
        clientes = session.query(Customer).all()

        data = []
        for cliente in clientes:
            transacoes = session.query(CashbackTransaction).filter(
                CashbackTransaction.customer_id == cliente.customer_id,
                CashbackTransaction.status == CashbackStatus.active,
                CashbackTransaction.valor > 0  # Apenas transações com saldo disponível
            ).all()

            saldo_total = sum(t.valor for t in transacoes)
            saldo_a_expirar = sum(t.valor for t in transacoes if t.expiration_date > agora)

            consolidado = {"🔴 <7 dias": 0.0, "🟡 7-15 dias": 0.0, "🟢 >15 dias": 0.0}
            for t in transacoes:
                dias_para_expirar = (t.expiration_date - agora).days
                if dias_para_expirar <= 7:
                    consolidado["🔴 <7 dias"] += t.valor
                elif dias_para_expirar <= 15:
                    consolidado["🟡 7-15 dias"] += t.valor
                else:
                    consolidado["🟢 >15 dias"] += t.valor

            # Adicionar informações consolidadas por cliente
            data.append({
                "Cliente": cliente.nome,
                "CPF": cliente.cpf,
                "Telefone": cliente.telefone,
                "Saldo Total (R$)": f"R${saldo_total:.2f}",
                "Saldo a Expirar (R$)": f"R${saldo_a_expirar:.2f}",
                "🔴 <7 dias (R$)": f"R${consolidado['🔴 <7 dias']:.2f}",
                "🟡 7-15 dias (R$)": f"R${consolidado['🟡 7-15 dias']:.2f}",
                "🟢 >15 dias (R$)": f"R${consolidado['🟢 >15 dias']:.2f}"
            })

        if not data:
            st.info("Nenhum saldo ativo próximo da expiração encontrado.")
        else:
            # Criar DataFrame consolidado
            df = pd.DataFrame(data).sort_values(by="Saldo Total (R$)", ascending=False)
            st.dataframe(df)

            st.download_button(
                label="Baixar Relatório em CSV",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="relatorio_expiracao_consolidado.csv",
                mime="text/csv"
            )
    
    session.close()
