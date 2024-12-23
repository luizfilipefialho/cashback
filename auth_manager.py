# auth_manager.py

import streamlit_authenticator as stauth
from data_manager import get_session, User
import os
from dotenv import load_dotenv

load_dotenv()

def get_authenticator():
    session = get_session()
    users = session.query(User).all()
    session.close()
    
    if not users:
        # Se não houver usuários, retorna um autenticador vazio
        credentials = {
            "usernames": {}
        }
    else:
        credentials = {
            "usernames": {}
        }
        for user in users:
            credentials["usernames"][user.username] = {
                "name": user.username,
                "password": user.hashed_password
            }
    
    authenticator = stauth.Authenticate(
        credentials=credentials,
        cookie_name='cashback_app',
        key=os.getenv("SECRET_KEY"),
        cookie_expiry_days=1
    )
    return authenticator

def get_current_user_id(username):
    session = get_session()
    user = session.query(User).filter(User.username == username).first()
    session.close()
    if user:
        return user.user_id
    return None
