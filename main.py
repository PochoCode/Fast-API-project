from fastapi import FastAPI
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from contextlib import asynccontextmanager
from sqlalchemy import create_engine
from config import settings
import modelos
from fastapi.middleware.cors import CORSMiddleware




@asynccontextmanager
async def lifespan(app: FastAPI):
    # Código que roda ANTES do servidor iniciar
    yield
    # Código que roda DEPOIS que o servidor parar
app=FastAPI(lifespan=lifespan)

origins = [
    "http://localhost",
    "http://localhost:8080", # Porta comum para desenvolvimento frontend
    "http://127.0.0.1:5500", # Porta padrão do Live Server do VSCode para o index.html
    "null", # Permite requisições de file:// (quando você abre o HTML diretamente)
    "*", # PERMITE TUDO (Use apenas para testes locais/desenvolvimento)
    # Adicione aqui a URL do seu frontend em produção
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



bcrypt_context= CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login_Auth")

from order_routes import orders
from order_auth import auths

app.include_router(orders)
app.include_router(auths)

#rodar isso no terminal : uvicorn main:app --reload
#RestAPIs

#Requisições CRUD:
#POST ->enviar/criar
#GET ->leitura/pegar
#Put/Patch->edição
#Delete->apagar
