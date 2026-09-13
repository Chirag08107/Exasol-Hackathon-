from fastapi import APIRouter, Depends

from utils.auth import get_current_user

router = APIRouter(
    prefix="/api/users",
    tags=["Users"]
)


@router.get("/me")
def get_current_user_info(
    user=Depends(get_current_user)
):
    return {
        "id": user["id"],
        "firstName": user["firstName"],
        "middleName": user["middleName"],
        "lastName": user["lastName"],
        "userName": user["userName"],
        "email": user["email"],
        "verified": user["verified"]
    }