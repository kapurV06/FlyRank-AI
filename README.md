## A4 — Auth with Supabase

Sign up, log in, log out, and two guarded routes — backed by Supabase Auth
as the identity provider. This server never hashes a password or signs a
token itself; it forwards credentials to Supabase and verifies the JWTs
Supabase hands back.

### Setup

1. Create a free project at [supabase.com](https://supabase.com).
2. **Project Settings → API** → copy the **Project URL** and the **`anon`
   public key** (never the `service_role` key — that one bypasses security).
3. **Authentication → Sign In / Providers → Email** → turn off **"Confirm
   email"** so a fresh signup can log in immediately (practice project only —
   leave it on in production).
4. `cp .env.example .env` and fill in `SUPABASE_URL` and `SUPABASE_KEY`.

### Run it

```
docker compose up
```

or locally:

```
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Swagger UI is at `http://localhost:8000/docs` — click **Authorize**, paste
an access token from `/auth/login`, then **Try it out** on any protected
route.

### Endpoints

| Method | Path                    | Auth required | Description                    |
|--------|-------------------------|:--:|----------------------------------------------|
| POST   | `/auth/signup`          | no  | Create a new user account            |
| POST   | `/auth/login`           | no  | Authenticate, returns access + refresh token |
| POST   | `/auth/logout`          | yes | Ends the session                     |
| GET    | `/public/info`          | no  | Open, unauthenticated data            |
| GET    | `/protected/profile`    | yes | Returns the caller's own profile      |
| GET    | `/protected/dashboard`  | yes | Second protected route — same guard, no new code |

### Example flow

```
$ curl -i -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
# 201

$ curl -i -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
# 200, returns access_token

$ curl -i http://localhost:8000/protected/profile \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
# 200

$ curl -i http://localhost:8000/protected/profile \
  -H "Authorization: Bearer tampered_token"
# 401 {"detail":"Invalid or expired token"}
```

*(Replace with your own real output and a Swagger screenshot before
submitting.)*

### 401 vs 403

`401` means "I don't know who you are" — no token, a malformed header, or
one Supabase can't verify. `403` would mean "I know exactly who you are,
and you still may not" — e.g. a non-admin hitting an admin-only route
(see the stretch goal). This assignment only implements `401`; a `403`
case is a stretch extra.

### Auth guard

`auth.py` holds the Supabase client and `get_current_user`, the one
function every protected route depends on (`user=Depends(get_current_user)`).
Adding a new locked door means adding that one line — see
`/protected/dashboard`, which reuses the exact same guard as `/protected/profile`.
