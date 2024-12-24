import streamlit as st
from data_manager import get_session, Customer, CashbackTransaction, CashbackUsage, CashbackStatus
from datetime import datetime, timedelta

def utilizar_saldo_page():
    st.title("💳 Utilizar Saldo de Cashback")

    session = get_session()

    # Selecionar Cliente
    clientes = session.query(Customer).all()
    if not clientes:
        st.info("Nenhum cliente cadastrado. Adicione um cliente primeiro.")
        session.close()
        return

    cliente_options = [f"{c.nome} - {c.cpf if c.cpf else 'Sem CPF'}" for c in clientes]
    cliente_selecionado = st.selectbox("Selecione o Cliente", cliente_options)

    if cliente_selecionado:
        cliente_nome, cliente_cpf = cliente_selecionado.split(" - ")
        cliente_cpf = cliente_cpf if cliente_cpf != 'Sem CPF' else None

        # Buscar cliente pelo CPF, Telefone ou Nome
        if cliente_cpf:
            customer = session.query(Customer).filter(Customer.cpf == cliente_cpf).first()
        else:
            customer = session.query(Customer).filter(Customer.nome == cliente_nome).first()

        # Caso o nome seja ambíguo, buscar pelo telefone
        if not customer:
            telefone_match = [c for c in clientes if c.nome == cliente_nome]
            if len(telefone_match) == 1:
                customer = telefone_match[0]
            else:
                st.error("Não foi possível identificar o cliente com os dados fornecidos.")
                customer = None

        if customer:
            # Calcular saldo total ativo
            transacoes = session.query(CashbackTransaction).filter(
                CashbackTransaction.customer_id == customer.customer_id,
                CashbackTransaction.status == CashbackStatus.active
            ).order_by(CashbackTransaction.expiration_date).all()

            saldo_total = sum(t.valor for t in transacoes)
            st.write(f"**Saldo Total Disponível:** R${saldo_total:.2f}")

            valor_compra = st.number_input("Valor da Nova Compra (R$)", min_value=0.01, step=0.01)
            id_nova_compra = st.text_input("ID da Nova Compra")  # Novo campo para o ID da nova compra

            if valor_compra > 0:
                limite_cashback = min(valor_compra * st.secrets["settings"]["CASHBACK_USAGE_LIMIT"], saldo_total)
                st.write(f"**Cashback Máximo Utilizável:** R${limite_cashback:.2f}")

                if st.button("Confirmar Utilização"):
                    if not id_nova_compra:
                        st.warning("Por favor, insira o ID da Nova Compra.")
                        return

                    # Atualizar transações e registrar o uso de cashback
                    valor_restante = limite_cashback
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

                    # Registrar o uso
                    usage = CashbackUsage(
                        customer_id=customer.customer_id,
                        used_value=limite_cashback,
                        used_at=datetime.utcnow(),
                        used_by=st.session_state["username"],
                        id_compra=id_nova_compra  # Registrar o ID da nova compra
                    )
                    session.add(usage)

                    # Calcular e adicionar novo cashback
                    valor_liquido = valor_compra - limite_cashback
                    novo_cashback = valor_liquido * st.secrets["settings"]["CASHBACK_PERCENTAGE"]
                    nova_transacao = CashbackTransaction(
                        customer_id=customer.customer_id,
                        valor=novo_cashback,
                        expiration_date=datetime.utcnow() + timedelta(days=30),
                        status=CashbackStatus.active,
                        created_by=st.session_state["username"],
                        id_compra=id_nova_compra  # Registrar o ID da nova compra
                    )
                    session.add(nova_transacao)

                    session.commit()
                    st.success(f"R${limite_cashback:.2f} utilizados. Novo cashback de R${novo_cashback:.2f} adicionado!")
        else:
            st.error("Cliente não encontrado. Verifique os dados e tente novamente.")

    session.close()
