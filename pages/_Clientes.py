import pandas as pd
import streamlit as st
from data_manager import get_session, Customer, CashbackTransaction, CashbackStatus
from datetime import datetime, timedelta
from urllib.parse import quote

def clientes_page():
    st.title("📇 Gestão de Clientes")
    
    menu = ["Adicionar Cliente", "Buscar Clientes"]
    choice = st.radio("Escolha uma opção", menu)
    
    session = get_session()
    
    if choice == "Adicionar Cliente":
        st.subheader("Adicionar Novo Cliente")
        nome = st.text_input("Nome")
        cpf = st.text_input("CPF")
        telefone = st.text_input("Telefone")
        
        if st.button("Salvar"):
            if nome and cpf and telefone:
                cliente_existente = session.query(Customer).filter(Customer.cpf == cpf).first()
                if cliente_existente:
                    st.error(f"O CPF {cpf} já está cadastrado para o cliente {cliente_existente.nome}.")
                else:
                    novo_cliente = Customer(nome=nome, cpf=cpf, telefone=telefone)
                    session.add(novo_cliente)
                    session.commit()
                    st.success(f"Cliente {nome} adicionado com sucesso!")
            else:
                st.warning("Por favor, preencha todos os campos.")
    
    elif choice == "Buscar Clientes":
        st.subheader("Lista de Clientes")
        busca = st.text_input("Digite o Nome ou CPF para buscar")
        
        if busca:
            clientes = session.query(Customer).filter(
                (Customer.nome.ilike(f"%{busca}%")) | 
                (Customer.cpf.ilike(f"%{busca}%"))
            ).all()
        else:
            clientes = session.query(Customer).all()
        
        if clientes:
            data = []
            for cliente in clientes:
                saldo_total = sum(t.valor for t in cliente.transactions if t.status == CashbackStatus.active)
                transacao_expiracao = min(
                    (t for t in cliente.transactions if t.status == CashbackStatus.active),
                    key=lambda t: t.expiration_date,
                    default=None
                )
                
                if transacao_expiracao:
                    data_expiracao = transacao_expiracao.expiration_date.strftime("%d/%m/%Y")
                else:
                    data_expiracao = "N/A"

                # Criar mensagem de WhatsApp
                mensagem = f"Olá {cliente.nome}, Tudo bem?\n\n" \
                           f"Você tem R${saldo_total:.2f} de cashback disponível na PEREGRINO com expiração em {data_expiracao}.\n" \
                           "Venha visitar nossa loja para resgatar!"
                mensagem_codificada = quote(mensagem)
                link_whatsapp = f"https://wa.me/55{cliente.telefone}?text={mensagem_codificada}"

                # Adicionar os dados na tabela
                data.append({
                    "Nome": cliente.nome,
                    "CPF": cliente.cpf,
                    "Telefone": cliente.telefone,
                    "Saldo Total (R$)": f"R${saldo_total:.2f}",
                    "Expiração Mais Próxima": data_expiracao,
                    "Contato": f"[Enviar WhatsApp]({link_whatsapp})"
                })

            # Exibir os dados em uma tabela
            df = pd.DataFrame(data)
            st.markdown(
                df.to_markdown(index=False),
                unsafe_allow_html=True
            )
        else:
            st.info("Nenhum cliente encontrado com os critérios de busca.")
    
    session.close()
