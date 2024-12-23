# data_manager.py

import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from dotenv import load_dotenv
from datetime import datetime, timedelta
import enum

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "cashback_app.db")
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Enum para status das transações
class CashbackStatus(enum.Enum):
    active = "active"
    expired = "expired"
    used = "used"

class Customer(Base):
    __tablename__ = "customers"
    customer_id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    cpf = Column(String, unique=True, index=True, nullable=False)
    telefone = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    transactions = relationship("CashbackTransaction", back_populates="customer")

class CashbackTransaction(Base):
    __tablename__ = "cashback_transactions"
    transaction_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    valor = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expiration_date = Column(DateTime, nullable=False)
    status = Column(Enum(CashbackStatus), default=CashbackStatus.active)
    used_at = Column(DateTime, nullable=True)
    used_value = Column(Float, nullable=True)

    customer = relationship("Customer", back_populates="transactions")

class CashbackExpired(Base):
    __tablename__ = "cashback_expired"
    expired_id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("cashback_transactions.transaction_id"), nullable=False)
    expired_date = Column(DateTime, default=datetime.utcnow)
    days_after_expiration = Column(Integer, nullable=False)

    transaction = relationship("CashbackTransaction")

class CashbackUsage(Base):
    __tablename__ = "cashback_usage"
    usage_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    used_value = Column(Float, nullable=False)
    used_at = Column(DateTime, default=datetime.utcnow)
    # used_by = Column(Integer, ForeignKey("users.user_id"), nullable=False)  # Remover se não rastrear usuários

    customer = relationship("Customer")
    # user = relationship("User")  # Remover se não rastrear usuários

def init_db():
    Base.metadata.create_all(bind=engine)

def get_session():
    return SessionLocal()

# Função para verificar e atualizar cashback expirado
def verificar_expirados():
    session = get_session()
    try:
        now = datetime.utcnow()
        expirados = session.query(CashbackTransaction).filter(
            CashbackTransaction.status == CashbackStatus.active,
            CashbackTransaction.expiration_date < now
        ).all()
        for transacao in expirados:
            transacao.status = CashbackStatus.expired
            dias_expirado = (now - transacao.expiration_date).days
            expired = CashbackExpired(
                transaction_id=transacao.transaction_id,
                expired_date=now,
                days_after_expiration=dias_expirado
            )
            session.add(expired)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Erro ao verificar expirados: {e}")
    finally:
        session.close()
