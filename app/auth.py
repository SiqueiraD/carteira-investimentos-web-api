from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from .database import usuarios
from fastapi import HTTPException
from bson import ObjectId
from .config import get_settings

settings = get_settings()

# Configurações de senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configurações JWT
SECRET_KEY = settings.JWT_SECRET
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha está correta."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Gera o hash da senha."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Cria um token JWT."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def autenticar_usuario(email: str, senha: str):
    """Autentica um usuário pelo email e senha."""
    user = usuarios.find_one({"email": email})
    if not user:
        return None
    if not verify_password(senha, user["senha"]):
        return None
    return user

def get_current_user(token: str, credentials_exception: HTTPException):
    """Obtém o usuário atual a partir do token JWT."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        tipo_usuario: str = payload.get("tipo_usuario")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = usuarios.find_one({"email": email})
    if user is None:
        raise credentials_exception
    
    return user
