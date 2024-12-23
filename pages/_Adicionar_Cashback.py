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
        id_compra = st.text_input("ID da Compra")  # Novo campo para o ID da compra
        
        # Obter o percentual de cashback do secrets.toml
        percentual_cashback = st.secrets["settings"]["CASHBACK_PERCENTAGE"]
        st.write(f"**Percentual de Cashback:** {percentual_cashback * 100:.2f}%")
        
        # Calcular o valor do cashback
        valor_cashback = valor_compra * percentual_cashback if valor_compra > 0 else 0.0
        st.write(f"**Valor do Cashback Calculado:** R${valor_cashback:.2f}")
        
        validade = st.number_input("Validade do Cashback (dias)", min_value=1, value=30)
        
        if st.button("Adicionar Cashback"):
            if valor_cashback > 0 and validade > 0 and id_compra:
                expiration_date = datetime.utcnow() + timedelta(days=int(validade))
                transacao = CashbackTransaction(
                    customer_id=customer.customer_id,
                    valor=valor_cashback,
                    expiration_date=expiration_date,
                    status=CashbackStatus.active,
                    created_by=st.session_state["username"],
                    id_compra=id_compra  # Registrar o ID da compra
                )
                session.add(transacao)
                session.commit()
                st.success(f"Cashback de R${valor_cashback:.2f} adicionado para {customer.nome}. Expira em {expiration_date.date()}.")
            else:
                st.warning("Preencha todos os campos corretamente.")
    
    session.close()
