import secrets
import string
from typing import Optional

from apis.auth.utils import update_user_password
from config import settings
from db.session import get_db
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

router = APIRouter()


# this is a highly sensitive endpoint used only for admin purposes
# it's excluded from the docs to make it more secure
@router.get(
    "/admin/reset-chef-password",
    include_in_schema=False,
    status_code=status.HTTP_200_OK,
)
def get_reset_chef_password(
    request: Request,
    db: Session = Depends(get_db),
    x_admin_reset_token: Optional[str] = Header(default=None),
):
    client_host = request.client.host if request.client else None

    # Only requests from the same machine are allowed
    # This endpoint is available only for Chef who is also our server admin!
    if client_host != "127.0.0.1":
        raise HTTPException(
            status_code=403,
            detail="Chef password can be reseted only from the local machine!",
        )

    # The peer address alone is not an authorization control: any local process
    # shares it. A pre-shared secret, provisioned out of band, is also required.
    # If no secret is configured, the endpoint is disabled.
    expected_token = settings.CHEF_PASSWORD_RESET_TOKEN
    if (
        not expected_token
        or not x_admin_reset_token
        or not secrets.compare_digest(
            x_admin_reset_token.encode("utf-8"), expected_token.encode("utf-8")
        )
    ):
        raise HTTPException(
            status_code=403,
            detail="Invalid or missing admin reset token!",
        )

    characters = string.ascii_letters + string.digits + "!@#$%^&*()_-+=;:[]"

    # generate a random password
    new_password = "".join(secrets.choice(characters) for i in range(32))
    update_user_password(db, settings.CHEF_USERNAME, new_password)

    return {"password": new_password}
