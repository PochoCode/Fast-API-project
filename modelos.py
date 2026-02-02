# %%
from sqlalchemy import create_engine, Column, String, Integer, Boolean, Float, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from config import settings
 
# A variável 'db' será inicializada no main.py durante o lifespan do app.
# Inicializa a engine imediatamente para que as dependências possam fazer o bind corretamente
db = create_engine(settings.DATABASE_URL)
#Criar a base do banco de dados

Base = declarative_base()

#Cria as clases(tabelas) do banco
#Usuario
class Usuario(Base):
    __tablename__="usuarios"
    id= Column("id", Integer, primary_key=True, autoincrement=True)
    nome= Column("nome", String)
    email= Column("email", String, nullable=False)
    
    senha= Column("senha", String)
    admin= Column("admin", Boolean, default=False)
    ativo= Column("ativo", Boolean, default=True)

    def __init__(self, nome, email, senha,  admin=False, ativo=True ) :
        self.nome = nome
        self.email= email
        self.senha= senha
        
        self.admin= admin
        self.ativo=ativo
#pedidos
#ESTADO_PEDIDO= (
#    ("pendente","pendente"),
#    ("cancelado","cancelado"),
#    ("terminado", "terminado")
#                )
class Pedidos(Base):
    __tablename__="pedidos"
    id= Column("id", Integer, primary_key=True, autoincrement=True)
    id_usuario= Column("id_usuario", ForeignKey("usuarios.id"))
    status= Column("status", String, default="pendente" )
    preco= Column("preco", Float, default=0)
    itens= relationship("Itenspedidos", cascade="all,delete")
   

    def __init__(self, id_usuario, status="pendente", preco=0):
        self.id_usuario= id_usuario
        self.status= status
        self.preco= preco
       
    def calcular_preco(self):
       #itens_pedido = session.query(Itenspedidos).filter(Itenspedidos.pedido == self.id).all()
       self.preco = sum(item.preco_unico * item.quantidade for item in self.itens)
       


#itenspedido
# VARIOS_TAMANHOS=(
#        ("simples","simples"),
#        ("completo","completo")
#    )

class Itenspedidos(Base):
  
    __tablename__="itens_pedidos"
    id= Column("id", Integer, primary_key=True, autoincrement=True)
    quantidade= Column("quantidade", Integer)
    tamanho= Column("tamanho", String)
    sabor= Column("sabor", String)
    preco_unico= Column("preco_unico", Float, default=0)
    id_pedido= Column("id_pedido", ForeignKey("pedidos.id"))

    def __init__(self, quantidade, tamanho, sabor, preco_unico, id_pedido):
        self.quantidade = quantidade
        self.tamanho= tamanho
        self.sabor= sabor
        self.preco_unico= preco_unico
        self.id_pedido= id_pedido
#Executa a criação dos metadados