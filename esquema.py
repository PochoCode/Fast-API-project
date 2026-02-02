# %%
from pydantic import BaseModel
from typing import Optional
class UsuarioEsquema(BaseModel) :
    nome: str
    email: str
    senha: str
    admin: bool = False
    ativo: bool = True
    class Config:
        from_attributes=True

class UsuarioCriacaoPublicaEsquema(BaseModel):
    """Esquema para a criação de usuários pela rota pública, sem o campo 'admin'."""
    nome: str
    email: str
    senha: str
    ativo: bool = True

    class Config:
        from_attributes=True


class PedidosEsquema(BaseModel):
    usuario: int
    
    class Config:
        from_attributes=True


class LoginEsquema(BaseModel):
    email: str
    senha: str
    class Config:
        from_attributes=True

class ItenspedidosEsquema(BaseModel):
    quantidade: int
    tamanho: str
    sabor: str
    preco_unico: float
    
    class config:
        from_attributes=True

class ResponsePedidosEsquema(BaseModel):
    id: int
    status: str
    preco: float
    itens: list[ItenspedidosEsquema] = []

    class Config:
        from_attributes = True


class ResponsePedidosEsquemalista(BaseModel):
    id: int
    id_usuario: int
    status: str
    preco: float
    itens: list[ItenspedidosEsquema] = []

    class Config:
        from_attributes = True
        