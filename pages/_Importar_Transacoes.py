import streamlit as st
import pandas as pd
from io import BytesIO
from data_manager import get_session, Customer, CashbackTransaction, CashbackStatus
from datetime import datetime, timedelta

def gerar_modelo_xlsx():
    """Cria um modelo de planilha Excel com os cabeçalhos corretos."""
    data = {
        "Nome": ["João Silva"],
        "CPF": ["12345678900"],
        "Telefone": ["11987654321"],
        "Valor": [100.00],
        "ID Compra": ["ABC123"],
        "Data Expiração": [datetime.utcnow().strftime("%Y-%m-%d")]
    }
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Modelo_Transacoes")
    return output.getvalue()

def importar_transacoes_page():
    st.title("📥 Importar Transações")

    # Botão para download do modelo de planilha
    st.download_button(
        label="📄 Baixar Modelo de Planilha",
        data=gerar_modelo_xlsx(),
        file_name="modelo_transacoes.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    uploaded_file = st.file_uploader("Envie um arquivo XLSX com as transações", type=["xlsx"])

    if uploaded_file:
        df = pd.read_excel(uploaded_file)

        # Validar se as colunas esperadas estão presentes
        required_columns = {"Nome", "CPF", "Telefone", "Valor", "ID Compra", "Data Expiração"}
        if not required_columns.issubset(df.columns):
            st.error(f"O arquivo deve conter as colunas obrigatórias: {', '.join(required_columns)}")
            return

        session = get_session()
        clientes_criados = 0
        transacoes_importadas = 0

        for _, row in df.iterrows():
            nome = str(row["Nome"]).strip()
            cpf = str(row["CPF"]).strip() if pd.notna(row["CPF"]) else None
            telefone = str(row["Telefone"]).strip() if pd.notna(row["Telefone"]) else None
            valor = float(row["Valor"])
            id_compra = str(row["ID Compra"]).strip() if pd.notna(row["ID Compra"]) else None
            expiration_date = pd.to_datetime(row["Data Expiração"]) if pd.notna(row["Data Expiração"]) else datetime.utcnow() + timedelta(days=30)

            # Verifica se o cliente já existe pelo CPF ou telefone
            cliente = None
            if cpf:
                cliente = session.query(Customer).filter(Customer.cpf == cpf).first()
            if not cliente and telefone:
                cliente = session.query(Customer).filter(Customer.telefone == telefone).first()
            
            # Se o cliente não existir, cria um novo
            if not cliente:
                cliente = Customer(nome=nome, cpf=cpf, telefone=telefone)
                session.add(cliente)
                session.commit()
                clientes_criados += 1
            
            # Adiciona a transação ao banco de dados
            transacao = CashbackTransaction(
                customer_id=cliente.customer_id,
                valor=valor,
                expiration_date=expiration_date,
                status=CashbackStatus.active,
                created_by=st.session_state.get("username", "Sistema"),
                id_compra=id_compra
            )
            session.add(transacao)
            transacoes_importadas += 1

        session.commit()
        session.close()

        st.success(f"Importação concluída! {clientes_criados} novos clientes adicionados e {transacoes_importadas} transações registradas.")
