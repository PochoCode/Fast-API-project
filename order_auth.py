# %%

from fastapi import APIRouter, Depends, HTTPException
from modelos import Usuario
from dependencias import criar_session, verificar_token
from main import bcrypt_context
from esquema import UsuarioEsquema, LoginEsquema, UsuarioCriacaoPublicaEsquema, ItenspedidosEsquema # Usaremos o esquema do arquivo 'esquema.py'
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordRequestForm


from config import settings

auths= APIRouter(prefix="/auth" , tags=["auth"])

def criar_token(id_usuario, duracao_token: timedelta = None):
    duracao = duracao_token or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    data_expiracao = datetime.now(timezone.utc) + duracao
    dic_info_token = {"sub":str(id_usuario), "exp":data_expiracao}
    token = jwt.encode(dic_info_token, settings.SECRET_KEY, settings.ALGORITHM)
    return token

def autenticar_usuario(email,senha,session):
    usuario= session.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        return False
    if not bcrypt_context.verify(senha, usuario.senha):
        return False

    return usuario


    


@auths.get("/")
async def auth():
    """
    Essa é a rota padrão de autenticação.
    """
    return {"mensagem":"Voce esta autenticando"}

@auths.get("/me", response_model=UsuarioEsquema)
async def ler_dados_usuario(usuario: Usuario = Depends(verificar_token)):
    """Retorna os dados do usuário logado."""
    return usuario

@auths.post("/criar_conta")
async def criar_conta(usuario_esquema: UsuarioCriacaoPublicaEsquema, session: Session = Depends(criar_session)):
    """
    Cria uma nova conta de usuário. Esta rota é pública.
    O campo 'admin' será ignorado e sempre definido como False por segurança.
    """
    print(Usuario)
    usuario = session.query(Usuario).filter(Usuario.email == usuario_esquema.email).first()
    if usuario:
        raise HTTPException(status_code=400, detail="E-mail ja cadastrado")

    senha_criptografada = bcrypt_context.hash(usuario_esquema.senha)
   
    novo_usuario = Usuario(
        nome=usuario_esquema.nome,
        email=usuario_esquema.email,
        senha=senha_criptografada,
        admin=False, # Camada extra de segurança, garantindo que o usuário nunca será admin
        ativo=usuario_esquema.ativo
    )
    session.add(novo_usuario)
    session.commit()
    return {"mensagem": f"Usuario cadastrado com sucesso {usuario_esquema.email}"}
    
@auths.post("/admin/criar_usuario", dependencies=[Depends(verificar_token)])
async def admin_criar_usuario(usuario_esquema: UsuarioEsquema, session: Session = Depends(criar_session), admin_logado: Usuario = Depends(verificar_token)):
    """
    Cria um novo usuário (incluindo administradores).
    Apenas usuários administradores podem acessar esta rota.
    """
    if not admin_logado.admin:
        raise HTTPException(status_code=403, detail="Acesso negado. Só admins podem criar usuários.")
    
    usuario_existente = session.query(Usuario).filter(Usuario.email == usuario_esquema.email).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado.")

    senha_criptografada = bcrypt_context.hash(usuario_esquema.senha)
    
    # Cria o novo usuário, respeitando o valor do campo 'admin' enviado
    novo_usuario = Usuario(
        nome=usuario_esquema.nome, email=usuario_esquema.email, senha=senha_criptografada,
        admin=usuario_esquema.admin, ativo=usuario_esquema.ativo
    )
    session.add(novo_usuario)
    session.commit()
    return {"mensagem": f"Usuário '{usuario_esquema.email}' criado com sucesso."}


@auths.post("/login")
async def login(login_esquema: LoginEsquema, session: Session = Depends(criar_session))   : 
    """
    Essa é a rota de login.Usando o email e a senha, o usuário será autenticado.
    """
    usuario = autenticar_usuario(login_esquema.email, login_esquema.senha, session) 
    if not usuario:
        raise HTTPException(status_code=400, detail="Usuario não encontrado ou credenciais invalidas")
    
    else:
        access_token= criar_token(usuario.id)
        refresh_token= criar_token(usuario.id, timedelta(days=7))
        return {
            "access_token":access_token,
            "refresh_token":refresh_token,
            "token_type":"bearer"
            }

@auths.post("/login_Auth")
async def login_Auth(dados_login: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(criar_session))   : 
    """
    Rota para autenticação usando OAuth2.
    Essa rota é privada e requer autenticação.
    """
    usuario = autenticar_usuario(dados_login.username, dados_login.password, session) 
    if not usuario:
        raise HTTPException(status_code=400, detail="Usuario não encontrado ou credenciais invalidas")
    
    else:
        access_token= criar_token(usuario.id)
        
        return {
            "access_token":access_token,
            "token_type":"bearer"
            }

@auths.get("/refresh")
async def  use_refresh_token(usuario: Usuario = Depends(verificar_token)):
    
    access_token = criar_token(usuario.id)
    return {
        "access_token": access_token,
          "token_type": "bearer"}
