from data_manager import get_session, Customer, CashbackTransaction, CashbackStatus
from datetime import datetime, timedelta
import pandas as pd

# Carregar dados da planilha
file_path = 'clientes.xlsx'
clientes_df = pd.read_excel(file_path)

# Converter os dados para lista de dicionários
clientes = clientes_df.to_dict(orient='records')

def adicionar_clientes_e_cashback():
    session = get_session()

    try:
        for cliente_data in clientes:
            telefone = str(cliente_data["telefone"])
            nome = cliente_data["Nome"]

            # Verificar se o cliente já existe pelo telefone
            cliente_existente = session.query(Customer).filter(Customer.telefone == telefone).first()

            if not cliente_existente:
                # Adicionar novo cliente
                novo_cliente = Customer(
                    nome=nome,
                    telefone=telefone,
                    cpf=None,  # Deixar CPF como None
                    created_at=datetime.utcnow()
                )
                session.add(novo_cliente)
                session.commit()
                cliente_id = novo_cliente.customer_id
                print(f"Cliente {nome} adicionado com sucesso!")
            else:
                cliente_id = cliente_existente.customer_id
                print(f"Cliente {nome} já existe no sistema.")

            # Adicionar transação de cashback
            if cliente_id is not None:
                data_compra = pd.to_datetime(cliente_data["Data Compra"]).to_pydatetime()
                expiration_date = data_compra + timedelta(days=30)

                # Validar campos obrigatórios antes de criar transação
                if cliente_data["Valor"] > 0 and cliente_data["ID Compra"]:
                    transacao = CashbackTransaction(
                        customer_id=cliente_id,
                        valor=cliente_data["Valor"],
                        created_at=data_compra,
                        expiration_date=expiration_date,
                        status=CashbackStatus.active,
                        id_compra=cliente_data["ID Compra"]
                    )
                    session.add(transacao)
                    session.commit()
                    print(f"Cashback de R${cliente_data['Valor']:.2f} adicionado para {nome}.")
                else:
                    print(f"Dados insuficientes para criar transação de cashback para {nome}.")

        print("Todos os clientes e cashbacks foram processados com sucesso.")
    except Exception as e:
        session.rollback()
        print(f"Erro ao processar: {e}")
    finally:
        session.close()

# Executar a função
adicionar_clientes_e_cashback()
