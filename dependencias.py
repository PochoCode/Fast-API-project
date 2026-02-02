from modelos import db
from sqlalchemy.orm import sessionmaker, Session
from fastapi import Depends, HTTPException
from modelos import Usuario
from jose import jwt, JWTError
from main import oauth2_scheme
from config import settings




# Crie a "fábrica de sessões" uma única vez aqui.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db)

def criar_session():
    """Dependência que cria e fecha uma sessão do banco de dados por requisição."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def verificar_token(token: str = Depends(oauth2_scheme), session: Session = Depends(criar_session)):
    try:
        dic_info= jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        id_usuario= dic_info.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado", headers={"WWW-Authenticate": "Bearer"})
    
    usuario= session.query(Usuario).filter(Usuario.id == int(id_usuario)).first()
    if not usuario:
        raise HTTPException(status_code=401, detail="Acceso invalido")
    
    return usuario
