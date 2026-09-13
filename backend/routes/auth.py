from fastapi import APIRouter, HTTPException, status,Depends

from utils.auth import get_current_user

from schemas.auth import (
    RegisterRequest,
    LoginRequest,
    VerifyRequest,
    GoogleLoginRequest,
    SendOtpRequest,
    VerifyOtpRequest
)

from services.auth_service import (
    register_user,
    authenticate_user,
    login_user,
    authenticate_google_user,
    send_otp,
    resend_otp,
    verify_otp,
    complete_user_verification
)


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)


@router.post("/register")
def register(data: RegisterRequest):

    try:

        user = register_user(data)

        return {
            "message": "Registration successful",
            "user": {
                "id": user["id"],
                "firstName": user["firstName"],
                "lastName": user["lastName"],
                "userName": user["userName"],
                "email": user["email"],
                "verified": user["verified"]
            }
        }

    except ValueError as e:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login")
def login(data: LoginRequest):

    user = authenticate_user(
        data.email,
        data.password
    )

    if user is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    return login_user(user)


@router.post("/verify")
def verify(data: VerifyRequest,
           user=Depends(get_current_user)
           ):

    try:
        updated_user = complete_user_verification(
            user["id"],
            data.phone,
            data.otp,
            data.address,
            data.aadhaarNumber
        )

        return {
            "message": "User verification completed successfully",
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

    except ValueError as e:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/logout")
def logout():

    return {
        "message": "Logout successful"
    }

@router.post("/google")
def google_login(data: GoogleLoginRequest):
    user = authenticate_google_user(data.credential)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google authentication"
        )

    return login_user(user)

@router.post("/send-otp")
def send_otp_route(
    data: SendOtpRequest,
    user=Depends(get_current_user)
):
    try:
        return send_otp(
            user["id"],
            data.phone
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/resend-otp")
def resend_otp_route(
    data: SendOtpRequest,
    user=Depends(get_current_user)
):
    try:
        return resend_otp(
            user["id"],
            data.phone
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/verify-otp")
def verify_otp_route(
    data: VerifyOtpRequest,
    user=Depends(get_current_user)
):
    try:
        return verify_otp(
            user["id"],
            data.phone,
            data.otp
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

