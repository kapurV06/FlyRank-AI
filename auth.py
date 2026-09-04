"""
auth.py — Supabase client and the reusable auth guard.

Every route that needs a logged-in user depends on get_current_user.
This is the one place token verification happens; add it to any route
by writing `user=Depends(get_current_user)` in that route's signature.
"""

import os
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# auto_error=False so we control the response ourselves — FastAPI's
# default for a missing header is 403, but this assignment wants 401
# for "no token", "malformed header", and "invalid token" alike.
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    if credentials is None or not credentials.credentials:
        raise HTTPException(status_code=401, detail="Access token required")

    token = credentials.credentials

    try:
        response = supabase.auth.get_user(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = getattr(response, "user", None)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return user
