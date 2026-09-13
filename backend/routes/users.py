from fastapi import APIRouter, Depends

from utils.auth import get_current_user
from schemas.user import UpdateProfileRequest
from services.auth_service import update_user_profile

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


@router.patch("/me")
def update_current_user_info(
    data: UpdateProfileRequest,
    user=Depends(get_current_user)
):
    updated_user = update_user_profile(
        user["id"],
        data.firstName,
        data.middleName,
        data.lastName,
        data.address
    )

    return {
        "message": "Profile updated successfully",
        "user": {
            "id": updated_user["id"],
            "firstName": updated_user["firstName"],
            "middleName": updated_user["middleName"],
            "lastName": updated_user["lastName"],
            "userName": updated_user["userName"],
            "email": updated_user["email"],
            "verified": updated_user["verified"]
        }
    }
