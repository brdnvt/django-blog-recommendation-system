import httpx
import json
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

import logging
import os

logger = logging.getLogger('auth')
logger.setLevel(logging.INFO)

JWKS_URL = os.environ.get('JWKS_URL', "http://127.0.0.1:8000/jwks") # url для отримання публічного ключа для верифікації JWT
security = HTTPBearer() # `Authorization` заголовок Bearer token

cached_jwks = None


async def get_jwk():
    """
    Отримання публічного ключа для верифікації JWT від JWKS серверу (в нашому випадку Django Rest Framework)
    :return: Публічний ключ JWKS
    """
    global cached_jwks
    if cached_jwks is None:
        try:
            logger.info(f"Fetching JWK from {JWKS_URL}")
            async with httpx.AsyncClient() as client:
                response = await client.get(JWKS_URL)
                if response.status_code != 200:
                    logger.error(f"Failed to fetch JWK: {response.status_code} {response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="JWK endpoint unavailable"
                    )
                jwks_data = response.json()
                if not jwks_data.get('keys') or len(jwks_data['keys']) == 0:
                    logger.error("No keys found in JWKS response")
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="No keys found in JWKS response"
                    )
                cached_jwks = jwks_data['keys'][0]
                logger.info("JWK fetched and cached successfully")
        except Exception as e:
            logger.error(f"Error fetching JWK: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Error fetching JWK"
            )
    
    return cached_jwks


async def verify_jwt(token: str):
    """
    Верифікації аутентичності JWT токену
    :param token: JWT токен
    :return: JWT payload
    """
    try:
        # Отримуємо публічний ключ для верифікації
        jwk = await get_jwk()
        
        # Перетворюємо JWK у формат, придатний для перевірки JWT
        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))
        
        logger.info("Verifying JWT token signature")
        
        # Декодуємо та верифікуємо JWT токен
        payload = jwt.decode(
            token,
            key=public_key,
            algorithms=['RS256'],  # Використовуємо RSA з SHA-256
            options={
                "verify_signature": True,  # Включаємо перевірку підпису
                "verify_exp": True,       # Перевіряємо термін дії
                "verify_aud": False,      # Не перевіряємо аудиторію (можна включити за потреби)
            }
        )
        
        logger.info(f"Token verified successfully for user_id: {payload.get('user_id')}")
        
        # Перевіряємо наявність обов'язкових полів
        if 'user_id' not in payload:
            logger.error("Token is missing required field 'user_id'")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid authentication token: missing user_id"
            )
        
        return payload
        
    except JWTError as e:
        logger.error(f"JWT validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid authentication token"
        )
    except Exception as e:
        logger.error(f"Unexpected error during token validation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Error validating token"
        )


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Отримання користувача з JWT токену
    :param credentials: credentials користувача (JWT токен)
    :return: user_id
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authentication credentials provided",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Верифікуємо токен та отримуємо payload
    payload = await verify_jwt(credentials.credentials)
    
    # Повертаємо user_id з токена
    return payload.get('user_id')
