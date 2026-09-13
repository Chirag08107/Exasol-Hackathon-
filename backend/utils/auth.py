from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from services.auth_service import get_user_by_id
from utils.security import decode_access_token


security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials"
    )

    try:

        token = credentials.credentials

        user_id = decode_access_token(token)

    except Exception:

        raise credentials_exception

    user = get_user_by_id(user_id)

    if user is None:
        raise credentials_exception

    return user