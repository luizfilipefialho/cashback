import streamlit as st
from data_manager import get_session, CashbackTransaction, Customer
from datetime import datetime, timedelta

def excluir_transacoes_page():
    st.title("🗑️ Excluir Transações")

    session = get_session()

    # Opções de exclusão
    metodo_exclusao = st.radio(
        "Escolha como deseja excluir transações:",
        ("Por Data", "Por ID de Compra", "Por Cliente")
    )

    if metodo_exclusao == "Por Data":
        st.subheader("Excluir Transações por Data")
        dias = st.number_input("Excluir transações dos últimos X dias:", min_value=1, value=1)
        limite_data = datetime.now() - timedelta(days=dias)

        if st.button("Excluir Transações"):
            deletadas = session.query(CashbackTransaction).filter(
                CashbackTransaction.created_at >= limite_data
            ).delete(synchronize_session=False)
            session.commit()
            st.success(f"{deletadas} transações excluídas com sucesso!")

    elif metodo_exclusao == "Por ID de Compra":
        st.subheader("Excluir Transações por ID de Compra")
        id_compra = st.text_input("Digite o ID da Compra")

        if st.button("Excluir Transações"):
            deletadas = session.query(CashbackTransaction).filter(
                CashbackTransaction.id_compra == id_compra
            ).delete(synchronize_session=False)
            session.commit()
            st.success(f"{deletadas} transações associadas ao ID de compra {id_compra} foram excluídas!")

    elif metodo_exclusao == "Por Cliente":
        st.subheader("Excluir Transações de um Cliente")
        
        clientes = session.query(Customer).all()
        cliente_opcoes = [f"{c.nome} - {c.cpf}" for c in clientes]
        cliente_selecionado = st.selectbox("Selecione o Cliente", cliente_opcoes)
        
        if cliente_selecionado:
            cpf_cliente = cliente_selecionado.split(" - ")[1]
            cliente = session.query(Customer).filter(Customer.cpf == cpf_cliente).first()

            if st.button("Excluir Transações"):
                deletadas = session.query(CashbackTransaction).filter(
                    CashbackTransaction.customer_id == cliente.customer_id
                ).delete(synchronize_session=False)
                session.commit()
                st.success(f"{deletadas} transações do cliente {cliente.nome} foram excluídas!")

    session.close()
