# %%
from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from dependencias import criar_session,verificar_token
from esquema import PedidosEsquema,  ItenspedidosEsquema, UsuarioCriacaoPublicaEsquema, UsuarioEsquema, ResponsePedidosEsquema, ResponsePedidosEsquemalista
from modelos import Pedidos, Usuario, Itenspedidos



orders = APIRouter(prefix="/ordens", tags=["ordens"],dependencies=[Depends(verificar_token)])

@orders.get("/")
async def ordens():
    """
    Essa é a rota padrão de pedidos onde com a função se comprovarão os pedidos.
    """
    
    return {"mensagem":"Voce acessou a lista de pedidos",
            "pedidos":"/ordens/listar"}

@orders.post("/pedido")
async def criar_pedido(session: Session= Depends(criar_session), usuario: Usuario = Depends(verificar_token)) :
    """Essa é a rota para criar um pedido. O usuário é identificado pelo token."""
    # Usa o ID do usuário autenticado (token)
    novo_pedido = Pedidos(id_usuario=usuario.id)
    session.add(novo_pedido)
    session.commit()
    return{"mensagem":f"Pedido criado com sucesso ID do pedido: {novo_pedido.id}"}

@orders.post("/pedido/cancelar/{id_pedido}")
async def cancelar_pedido(id_pedido: int, session: Session=Depends(criar_session), usuario: Usuario = Depends(verificar_token)):
    """Essa é a rota para cancelar um pedido, indique um usuario existente e o id do pedido a cancelar,este sera deletado"""
    pedido = session.query(Pedidos).filter(Pedidos.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")
    
    if not usuario.admin and pedido.id_usuario != usuario.id:
        raise HTTPException(status_code=401, detail="Você não tem permissão para cancelar este pedido")
    
    pedido.status = "cancelado"
    session.delete(pedido)
    session.commit()
    return {"mensagem": f"Pedido numero {pedido.id} cancelado com sucesso",
            "pedido": pedido}

@orders.get("/listar", response_model=list[ResponsePedidosEsquemalista])
async def listar_todos_pedidos_admin(session : Session= Depends(criar_session), usuario: Usuario = Depends(verificar_token)):
    """Essa é a rota para listar todos os pedidos"""
    if not usuario.admin:
        raise HTTPException(status_code=401, detail="Você não tem permissão para listar pedidos")
    else:
        pedidos = session.query(Pedidos).all()
        
        return pedidos


@orders.post("/pedido/adicionar-item/{id_pedido}")
async def adicionar_item_pedido(id_pedido: int, itens_pedido_esquema : ItenspedidosEsquema, session: Session=Depends(criar_session), usuario: Usuario = Depends(verificar_token)):
    """Essa é a rota para adicionar um item ao pedido autentique o usuario e indique um pedido existente"""
    pedido= session.query(Pedidos).filter(Pedidos.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")
    if not usuario.admin and usuario.id != pedido.id_usuario:
        raise HTTPException(status_code=401, detail="Você não tem permissão para adicionar itens a este pedido")
    item_pedido= Itenspedidos(
        itens_pedido_esquema.quantidade,
        itens_pedido_esquema.tamanho,
        itens_pedido_esquema.sabor,
        itens_pedido_esquema.preco_unico,
        id_pedido
    )
   
    
    session.add(item_pedido)
    session.commit()
    session.refresh(pedido) # Atualiza o objeto 'pedido' para carregar o novo item na relação

    pedido.calcular_preco() # Agora calcula o preço com o novo item já incluído
    session.commit() # Salva o preço atualizado no banco de dados

    return {"mensagem": f"Item adicionado ao pedido {id_pedido} com sucesso",
            "preço":pedido.preco}

@orders.post("/pedido/remover-item/{id_item_pedido}")
async def remover_item_pedido(id_item_pedido: int,  session: Session=Depends(criar_session), usuario: Usuario = Depends(verificar_token)):
    """Essa é a rota para remover os item dos pedidos"""
    item_pedido= session.query(Itenspedidos).filter(Itenspedidos.id == id_item_pedido).first()
    pedido = session.query(Pedidos).filter(Pedidos.id == item_pedido.id_pedido).first()
    if not item_pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")
    if not usuario.admin and usuario.id != pedido.id_usuario:
        raise HTTPException(status_code=401, detail="Você não tem permissão para adicionar itens a este pedido")

    
    session.delete(item_pedido)
    session.commit()
    session.refresh(pedido) # Atualiza o objeto 'pedido' para carregar o novo item na relação

    pedido.calcular_preco() # Agora calcula o preço com o novo item já incluído
    session.commit() # Salva o preço atualizado no banco de dados
    return {"mensagem": f"Item removido ao pedido {id_item_pedido} com sucesso",
            "itens_pedido":len(pedido.itens),
            "pedido":pedido}

@orders.post("/pedido/terminar/{id_pedido}")
async def finalizar_pedido(id_pedido: int, session: Session=Depends(criar_session), usuario: Usuario = Depends(verificar_token)):

    pedido = session.query(Pedidos).filter(Pedidos.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")
    
    if not usuario.admin and pedido.id_usuario != usuario.id:
        raise HTTPException(status_code=401, detail="Você não tem permissão para cancelar este pedido")
    
    pedido.status = "FINALIZADO"
   
    session.commit()
    return {"mensagem": f"Pedido numero {pedido.id} finalizado com sucesso",
            "pedido": pedido}

@orders.get("/pedido/{id_pedido}")
async def visualizar_pedido(id_pedido: int, session: Session=Depends(criar_session), usuario: Usuario = Depends(verificar_token)):
    pedido = session.query(Pedidos).filter(Pedidos.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")
    
    if not usuario.admin and pedido.id_usuario != usuario.id:
        raise HTTPException(status_code=401, detail="Você não tem permissão para cancelar este pedido")
    
    return {
        "itens_pedido":len(pedido.itens),
        "pedido":pedido
    }


@orders.get("/listar/pedidos-usuarios", response_model=list[ResponsePedidosEsquema])
async def listar_meus_pedidos( session : Session= Depends(criar_session), usuario: Usuario = Depends(verificar_token)):
  
        pedidos = session.query(Pedidos).filter(Pedidos.id_usuario == usuario.id).all()
        
        
        return pedidos