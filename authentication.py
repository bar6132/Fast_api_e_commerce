import jwt
from passlib.context import CryptContext
from dotenv import dotenv_values
from models import User
from fastapi import status, HTTPException

config_credential = dotenv_values(".env")

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def get_hashed_password(password):
    return pwd_context.hash(password)


async def verified_token(token: str):
    try:
        payload = jwt.decode(token, config_credential['SECRET'], algorithms=['HS256'])
        print("Decoded payload:", payload)  # Print the decoded payload for debugging
        user = await User.get(id=payload.get("id"))
        return user
    except jwt.DecodeError as e:
        print("JWT decode error:", e)  # Print the specific decoding error for debugging
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        print("Token verification error:", e)  # Print other exceptions for debugging
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification failed",
            headers={"WWW-Authenticate": "Bearer"}
        )


async def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


async def authenticate_user(username: str, password: str):
    user = await User.get(username=username)  # Assuming this is an async function to get user from DB
    if user and await verify_password(password, user.password):  # Await verify_password here
        return user
    return False


async def token_generator(username: str, password: str):
    user = await authenticate_user(username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid username or password',
            headers={"WWW-Authenticate": "Bearer"}
        )

    token_data ={
        "id": user.id,
        "username": user.username
    }
    token = jwt.encode(token_data, config_credential['SECRET'])

    return token
