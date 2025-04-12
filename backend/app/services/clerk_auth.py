# import jwt
# import requests
# # from jwt.algorithms import RSAAlgorithm

# # Replace this with your actual Clerk domain (no trailing slash)
# CLERK_JWKS_URL = "https://cmucal-456604.clerk.accounts.dev/.well-known/jwks.json"
# CLERK_AUDIENCE = "<your-clerk-frontend-api>"  # e.g., "https://cmucal.clerk.accounts.dev"

# _cached_public_key = None

# def get_clerk_public_key():
#     global _cached_public_key
#     if _cached_public_key:
#         return _cached_public_key

#     jwks = requests.get(CLERK_JWKS_URL).json()
#     jwk = jwks["keys"][0]  # take the first key
#     _cached_public_key = RSAAlgorithm.from_jwk(jwk)
#     return _cached_public_key

# def verify_clerk_token(token: str) -> str:
#     """
#     Verifies Clerk-issued RS256 JWT and returns the Clerk user ID (`sub`).
#     """
#     public_key = get_clerk_public_key()
#     decoded = jwt.decode(
#         token,
#         public_key,
#         algorithms=["RS256"],
#         audience=CLERK_AUDIENCE,
#     )
#     return decoded["sub"]