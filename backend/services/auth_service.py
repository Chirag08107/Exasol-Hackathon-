import os
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

import requests
import pyexasol

from dotenv import load_dotenv
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from database.exasol import get_connection
from database.mock_db import otp_sessions

from utils.security import (
    hash_password,
    verify_password,
    create_access_token
)


load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
TWOFACTOR_API_KEY = os.getenv("TWOFACTOR_API_KEY")


def get_user_by_id(user_id: int):

    connection = get_connection()

    try:

        result = connection.execute(
            """
            SELECT
                user_id,
                first_name,
                middle_name,
                last_name,
                username,
                email,
                password_hash,
                google_sub,
                phone,
                address,
                aadhaar_number,
                verified
            FROM FORM_APP.USER_ACCOUNT
            WHERE user_id = {user_id}
            """,
            {
                "user_id": user_id
            }
        ).fetchall()

        if not result:
            return None

        row = result[0]

        return {
            "id": row[0],
            "firstName": row[1],
            "middleName": row[2],
            "lastName": row[3],
            "userName": row[4],
            "email": row[5],
            "password_hash": row[6],
            "google_sub": row[7],
            "phone": row[8],
            "address": row[9],
            "aadhaarNumber": row[10],
            "verified": bool(row[11])
        }

    finally:
        connection.close()


def update_user_profile(
    user_id: int,
    first_name: str,
    middle_name: str | None,
    last_name: str,
    address: str | None
):
    connection = get_connection()

    try:
        connection.execute(
            """
            UPDATE FORM_APP.USER_ACCOUNT
            SET
                first_name = {first_name},
                middle_name = {middle_name},
                last_name = {last_name},
                address = COALESCE({address}, address)
            WHERE user_id = {user_id}
            """,
            {
                "first_name": first_name,
                "middle_name": middle_name,
                "last_name": last_name,
                "address": address,
                "user_id": user_id
            }
        )

        connection.commit()

    finally:
        connection.close()

    return get_user_by_id(user_id)


def register_user(data):

    connection = get_connection()

    try:

        # Check email
        result = connection.execute(
            """
            SELECT user_id
            FROM FORM_APP.USER_ACCOUNT
            WHERE email = {email}
            """,
            {
                "email": str(data.email)
            }
        ).fetchall()

        if result:
            raise ValueError("Email already registered")

        # Check username
        result = connection.execute(
            """
            SELECT user_id
            FROM FORM_APP.USER_ACCOUNT
            WHERE username = {username}
            """,
            {
                "username": data.userName
            }
        ).fetchall()

        if result:
            raise ValueError("Username already taken")

        # Generate new user ID
        result = connection.execute(
            """
            SELECT COALESCE(MAX(user_id), 0) + 1
            FROM FORM_APP.USER_ACCOUNT
            """
        ).fetchall()

        user_id = result[0][0]

        password = hash_password(data.password)

        connection.execute(
            """
            INSERT INTO FORM_APP.USER_ACCOUNT
            (
                user_id,
                first_name,
                middle_name,
                last_name,
                username,
                email,
                password_hash,
                google_sub,
                phone,
                address,
                aadhaar_number,
                verified
            )
            VALUES
            (
                {user_id},
                {first_name},
                {middle_name},
                {last_name},
                {username},
                {email},
                {password_hash},
                NULL,
                NULL,
                NULL,
                NULL,
                FALSE
            )
            """,
            {
                "user_id": user_id,
                "first_name": data.firstName,
                "middle_name": data.middleName,
                "last_name": data.lastName,
                "username": data.userName,
                "email": str(data.email),
                "password_hash": password
            }
        )

        connection.commit()

    finally:
        connection.close()

    return get_user_by_id(user_id)


def authenticate_user(email, password):

    connection = get_connection()

    try:

        result = connection.execute(
            """
            SELECT
                user_id,
                first_name,
                middle_name,
                last_name,
                username,
                email,
                password_hash,
                google_sub,
                phone,
                address,
                aadhaar_number,
                verified
            FROM FORM_APP.USER_ACCOUNT
            WHERE email = {email}
            """,
            {
                "email": str(email)
            }
        ).fetchall()

        if not result:
            return None

        row = result[0]

        user = {
            "id": row[0],
            "firstName": row[1],
            "middleName": row[2],
            "lastName": row[3],
            "userName": row[4],
            "email": row[5],
            "password_hash": row[6],
            "google_sub": row[7],
            "phone": row[8],
            "address": row[9],
            "aadhaarNumber": row[10],
            "verified": bool(row[11])
        }

        if not user["password_hash"]:
            return None

        if verify_password(
            password,
            user["password_hash"]
        ):
            return user

        return None

    finally:
        connection.close()


def login_user(user):

    token = create_access_token(user["id"])

    safe_user = {
        "id": user["id"],
        "firstName": user["firstName"],
        "middleName": user["middleName"],
        "lastName": user["lastName"],
        "userName": user["userName"],
        "email": user["email"],
        "verified": user["verified"]
    }

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": safe_user
    }


def authenticate_google_user(credential):

    try:

        google_user = id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            GOOGLE_CLIENT_ID
        )

    except Exception:

        return None

    google_sub = google_user.get("sub")
    email = google_user.get("email")
    email_verified = google_user.get(
        "email_verified",
        False
    )

    if not google_sub or not email:
        return None

    if not email_verified:
        return None

    connection = get_connection()

    try:

        # Check Google account
        result = connection.execute(
            """
            SELECT user_id
            FROM FORM_APP.USER_ACCOUNT
            WHERE google_sub = {google_sub}
            """,
            {
                "google_sub": google_sub
            }
        ).fetchall()

        if result:
            return get_user_by_id(result[0][0])

        # Check whether email already exists
        result = connection.execute(
            """
            SELECT user_id
            FROM FORM_APP.USER_ACCOUNT
            WHERE email = {email}
            """,
            {
                "email": email
            }
        ).fetchall()

        if result:

            user_id = result[0][0]

            connection.execute(
                """
                UPDATE FORM_APP.USER_ACCOUNT
                SET google_sub = {google_sub}
                WHERE user_id = {user_id}
                """,
                {
                    "google_sub": google_sub,
                    "user_id": user_id
                }
            )

            connection.commit()

            return get_user_by_id(user_id)

        # Create new Google user
        result = connection.execute(
            """
            SELECT COALESCE(MAX(user_id), 0) + 1
            FROM FORM_APP.USER_ACCOUNT
            """
        ).fetchall()

        user_id = result[0][0]

        username = email.split("@")[0]

        # Make username unique if necessary
        original_username = username
        counter = 1

        while True:

            result = connection.execute(
                """
                SELECT user_id
                FROM FORM_APP.USER_ACCOUNT
                WHERE username = {username}
                """,
                {
                    "username": username
                }
            ).fetchall()

            if not result:
                break

            username = (
                f"{original_username}{counter}"
            )

            counter += 1

        connection.execute(
            """
            INSERT INTO FORM_APP.USER_ACCOUNT
            (
                user_id,
                first_name,
                middle_name,
                last_name,
                username,
                email,
                password_hash,
                google_sub,
                phone,
                address,
                aadhaar_number,
                verified
            )
            VALUES
            (
                {user_id},
                {first_name},
                NULL,
                {last_name},
                {username},
                {email},
                NULL,
                {google_sub},
                NULL,
                NULL,
                NULL,
                FALSE
            )
            """,
            {
                "user_id": user_id,
                "first_name": google_user.get(
                    "given_name",
                    ""
                ),
                "last_name": google_user.get(
                    "family_name",
                    ""
                ),
                "username": username,
                "email": email,
                "google_sub": google_sub
            }
        )

        connection.commit()

        return get_user_by_id(user_id)

    finally:
        connection.close()


def send_otp(user_id: int, phone: str):

    if not TWOFACTOR_API_KEY:
        raise ValueError(
            "2Factor API key is not configured"
        )

    phone = phone.strip()

    if not phone.startswith("+"):
        raise ValueError(
            "Phone number must be in international format, "
            "e.g. +919876543210"
        )

    encoded_phone = quote(phone, safe="")

    url = (
        f"https://2factor.in/API/V1/"
        f"{TWOFACTOR_API_KEY}/SMS/"
        f"{encoded_phone}/AUTOGEN"
    )

    try:

        response = requests.get(
            url,
            timeout=15
        )

        response_data = response.json()

    except Exception:

        raise ValueError(
            "Unable to connect to OTP service"
        )

    if response_data.get("Status") != "Success":

        raise ValueError(
            response_data.get(
                "Details",
                "Failed to send OTP"
            )
        )

    session_id = response_data.get("Details")

    if not session_id:
        raise ValueError(
            "OTP service did not return a session ID"
        )

    now = datetime.now(timezone.utc)

    otp_sessions[user_id] = {
        "phone": phone,
        "session_id": session_id,
        "sent_at": now,
        "expires_at": now + timedelta(minutes=5),
        "resend_available_at": (
            now + timedelta(seconds=60)
        ),
        "phone_verified": False
    }

    return {
        "message": "OTP sent successfully",
        "expires_in": 300,
        "resend_after": 60
    }


def verify_otp(
    user_id: int,
    phone: str,
    otp: str
):

    session = otp_sessions.get(user_id)

    if not session:
        raise ValueError(
            "Please request an OTP first"
        )

    if session["phone"] != phone:
        raise ValueError(
            "Phone number does not match "
            "the OTP request"
        )

    if session["phone_verified"]:

        return {
            "message": "Phone number already verified",
            "phone_verified": True
        }

    now = datetime.now(timezone.utc)

    if now > session["expires_at"]:

        del otp_sessions[user_id]

        raise ValueError(
            "OTP has expired. Please request a new OTP"
        )

    otp = otp.strip()

    if not otp.isdigit():
        raise ValueError(
            "OTP must contain only digits"
        )

    session_id = session["session_id"]

    encoded_session = quote(
        session_id,
        safe=""
    )

    encoded_otp = quote(
        otp,
        safe=""
    )

    url = (
        f"https://2factor.in/API/V1/"
        f"{TWOFACTOR_API_KEY}/SMS/VERIFY/"
        f"{encoded_session}/{encoded_otp}"
    )

    try:

        response = requests.get(
            url,
            timeout=15
        )

        response_data = response.json()

    except Exception:

        raise ValueError(
            "Unable to connect to OTP service"
        )

    if response_data.get("Status") != "Success":

        raise ValueError(
            response_data.get(
                "Details",
                "Invalid OTP"
            )
        )

    session["phone_verified"] = True

    return {
        "message": "Phone number verified successfully",
        "phone_verified": True
    }


def resend_otp(user_id: int, phone: str):

    session = otp_sessions.get(user_id)

    if session:

        now = datetime.now(timezone.utc)

        if now < session["resend_available_at"]:

            remaining = int(
                (
                    session["resend_available_at"]
                    - now
                ).total_seconds()
            )

            raise ValueError(
                f"Please wait {remaining} seconds "
                "before requesting another OTP"
            )

    return send_otp(
        user_id,
        phone
    )

def complete_user_verification(
    user_id: int,
    phone: str,
    otp: str,
    address: str,
    aadhaar_number: str
):

    phone = phone.strip()
    otp = otp.strip()
    address = address.strip()
    aadhaar_number = aadhaar_number.strip()

    if not phone:
        raise ValueError("Phone number is required")

    if not address:
        raise ValueError("Address is required")

    if not aadhaar_number:
        raise ValueError("Aadhaar number is required")

    # Check that this user's OTP was successfully verified
    otp_session = otp_sessions.get(user_id)

    if not otp_session:
        raise ValueError(
            "Please verify your phone number first"
        )

    if otp_session["phone"] != phone:
        raise ValueError(
            "Phone number does not match the OTP verification"
        )

    if not otp_session["phone_verified"]:
        raise ValueError(
            "Please verify your phone number first"
        )

    # Get the user from Exasol
    user = get_user_by_id(user_id)

    if user is None:
        raise ValueError("User not found")

    connection = get_connection()

    try:

        connection.execute(
            """
            UPDATE FORM_APP.USER_ACCOUNT
            SET
                phone = {phone},
                address = {address},
                aadhaar_number = {aadhaar_number},
                verified = TRUE
            WHERE user_id = {user_id}
            """,
            {
                "phone": phone,
                "address": address,
                "aadhaar_number": aadhaar_number,
                "user_id": user_id
            }
        )

        connection.commit()

    finally:
        connection.close()

    # OTP has served its purpose
    otp_sessions.pop(user_id, None)

    updated_user = get_user_by_id(user_id)

    return updated_user