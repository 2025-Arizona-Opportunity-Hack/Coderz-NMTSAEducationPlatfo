"""
Auth0 JWT Authentication for Django REST Framework

This module provides authentication using Auth0 JWT tokens (RS256).
Validates tokens using JWKS from Auth0 and provisions users on first request.
"""

import jwt
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import authentication, exceptions
from functools import lru_cache
from typing import Optional, Dict, Any

User = get_user_model()


@lru_cache(maxsize=1)
def get_jwks() -> Dict[str, Any]:
    """
    Fetch JWKS from Auth0 and cache it.
    
    Returns:
        dict: JWKS data from Auth0
        
    Raises:
        Exception: If JWKS cannot be fetched
    """
    auth0_domain = settings.AUTH0_DOMAIN
    if not auth0_domain:
        raise ValueError("AUTH0_DOMAIN is not configured")
    
    jwks_url = f"https://{auth0_domain}/.well-known/jwks.json"
    
    try:
        response = requests.get(jwks_url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise Exception(f"Failed to fetch JWKS: {str(e)}")


def get_signing_key(token: str) -> str:
    """
    Extract the signing key from JWKS for the given token.
    
    Args:
        token: JWT token string
        
    Returns:
        str: PEM-encoded signing key
        
    Raises:
        Exception: If signing key cannot be found
    """
    try:
        # Decode header without verification to get kid
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        
        if not kid:
            raise Exception("No kid in token header")
        
        # Get JWKS
        jwks = get_jwks()
        
        # Find matching key
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                # Convert JWK to PEM
                return jwt.algorithms.RSAAlgorithm.from_jwk(key)
        
        raise Exception(f"No matching key found for kid: {kid}")
        
    except Exception as e:
        raise Exception(f"Failed to get signing key: {str(e)}")


def provision_user_from_token(token_payload: Dict[str, Any]) -> User:
    """
    Provision or update user from Auth0 token payload.
    
    Args:
        token_payload: Decoded JWT payload
        
    Returns:
        User: Django user instance
    """
    # Extract user info from token
    auth0_sub = token_payload.get("sub")
    email = token_payload.get("email")
    
    if not auth0_sub:
        raise exceptions.AuthenticationFailed("Token missing 'sub' claim")
    
    if not email:
        raise exceptions.AuthenticationFailed("Token missing 'email' claim")
    
    # Extract roles from custom claim
    # Auth0 Action should add roles as: https://nmtsa.org/roles
    roles_claim = settings.AUTH0_ROLES_CLAIM
    roles = token_payload.get(roles_claim, [])
    
    # Default role if none provided
    if not roles:
        roles = ["student"]
    
    # Use first role as primary (student, teacher, admin)
    primary_role = roles[0] if isinstance(roles, list) else roles
    
    # Map Auth0 sub to user
    try:
        # Try to find user by Auth0 sub
        user = User.objects.get(username=auth0_sub)
        
        # Update email and role if changed
        user.email = email
        user.role = primary_role
        user.save()
        
    except User.DoesNotExist:
        # Try to find by email (for existing users)
        try:
            user = User.objects.get(email=email)
            # Link Auth0 sub to existing user
            user.username = auth0_sub
            user.role = primary_role
            user.save()
        except User.DoesNotExist:
            # Create new user
            user = User.objects.create(
                username=auth0_sub,
                email=email,
                role=primary_role,
                full_name=token_payload.get("name", email.split("@")[0]),
                is_active=True,
            )
            
            # Set unusable password (OAuth only)
            user.set_unusable_password()
            user.save()
    
    # Sync roles to Django groups
    from django.contrib.auth.models import Group
    
    # Clear existing groups
    user.groups.clear()
    
    # Add user to role-based groups
    for role in roles if isinstance(roles, list) else [roles]:
        group, _ = Group.objects.get_or_create(name=role)
        user.groups.add(group)
    
    return user


class Auth0JWTAuthentication(authentication.BaseAuthentication):
    """
    Auth0 JWT Authentication class for DRF.
    
    Validates RS256 JWT tokens from Auth0 using JWKS.
    Provisions users automatically on first request.
    """
    
    def authenticate(self, request):
        """
        Authenticate request using Auth0 JWT token.
        
        Args:
            request: Django request object
            
        Returns:
            tuple: (user, None) if authenticated
            None: If no auth header present
            
        Raises:
            AuthenticationFailed: If token is invalid
        """
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        
        if not auth_header:
            return None
        
        parts = auth_header.split()
        
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return None
        
        token = parts[1]
        
        try:
            # Get signing key
            signing_key = get_signing_key(token)
            
            # Verify and decode token
            auth0_domain = settings.AUTH0_DOMAIN
            auth0_audience = settings.AUTH0_AUDIENCE
            auth0_issuer = f"https://{auth0_domain}/"
            
            payload = jwt.decode(
                token,
                signing_key,
                algorithms=["RS256"],
                audience=auth0_audience,
                issuer=auth0_issuer,
            )
            
            # Provision or get user
            user = provision_user_from_token(payload)
            
            return (user, None)
            
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Token has expired")
        except jwt.InvalidAudienceError:
            raise exceptions.AuthenticationFailed("Invalid token audience")
        except jwt.InvalidIssuerError:
            raise exceptions.AuthenticationFailed("Invalid token issuer")
        except jwt.InvalidSignatureError:
            raise exceptions.AuthenticationFailed("Invalid token signature")
        except jwt.DecodeError:
            raise exceptions.AuthenticationFailed("Invalid token format")
        except Exception as e:
            raise exceptions.AuthenticationFailed(f"Authentication failed: {str(e)}")
    
    def authenticate_header(self, request):
        """
        Return WWW-Authenticate header for 401 responses.
        """
        return 'Bearer realm="api"'
