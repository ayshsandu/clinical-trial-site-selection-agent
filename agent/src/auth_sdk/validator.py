import ssl
import jwt
from jwt import PyJWKClient
from typing import Optional, List, Union
from .models import TokenConfig
from .logger import setup_logger


class TokenValidationError(Exception):
    """Base exception for token validation errors."""
    pass


class TokenExpiredError(TokenValidationError):
    """Token has expired."""
    pass


class InvalidTokenError(TokenValidationError):
    """Token is invalid."""
    pass


class ScopeValidationError(TokenValidationError):
    """Required scope not found in token."""
    pass


class TokenValidator:
    def __init__(self, config: TokenConfig):
        self.config = config
        
        ssl_context = None
        if config.ssl_verify is False:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
        elif isinstance(config.ssl_verify, str):
            ssl_context = ssl.create_default_context(cafile=config.ssl_verify)
            
        self.jwks_client = PyJWKClient(config.jwks_url, ssl_context=ssl_context)
        self.logger = setup_logger(__name__, config.log_level)

    def validate(
        self, 
        token: str, 
        verify_audience: bool = True,
        verify_issuer: bool = True
    ) -> dict:
        """
        Validate a JWT token.
        
        Args:
            token: JWT token string
            verify_audience: Whether to verify the audience claim
            verify_issuer: Whether to verify the issuer claim
            
        Returns:
            dict: Decoded JWT payload
            
        Raises:
            TokenExpiredError: If token has expired
            InvalidTokenError: If token is invalid
        """
        try:
            self.logger.debug("Fetching signing key from JWKS")
            signing_key = self.jwks_client.get_signing_key_from_jwt(token)
            
            # Build decode options
            options = {
                "verify_aud": verify_audience,
                "verify_iss": verify_issuer,
            }
            
            # Prepare kwargs for decode
            decode_kwargs = {
                "algorithms": ["RS256"],
                "options": options,
            }
            
            # Add audience and issuer if verification is enabled
            if verify_audience and self.config.audience:
                decode_kwargs["audience"] = self.config.audience
            if verify_issuer and self.config.issuer:
                decode_kwargs["issuer"] = self.config.issuer
            
            data = jwt.decode(
                token,
                signing_key.key,
                **decode_kwargs
            )
            self.logger.debug("Token validation successful")
            return data
            
        except jwt.ExpiredSignatureError as e:
            self.logger.warning("Token has expired")
            raise TokenExpiredError("Token has expired") from e
        except jwt.InvalidTokenError as e:
            self.logger.warning(f"Invalid token: {str(e)}")
            raise InvalidTokenError(f"Invalid token: {str(e)}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error during token validation: {str(e)}")
            raise InvalidTokenError(f"Token validation failed: {str(e)}") from e

    def validate_with_scope(
        self,
        token: str,
        required_scope: Union[str, List[str]],
        verify_audience: bool = True,
        verify_issuer: bool = True
    ) -> dict:
        """
        Validate a JWT token and check for required scope(s).
        
        Args:
            token: JWT token string
            required_scope: Required scope(s) - can be a string or list of strings
            verify_audience: Whether to verify the audience claim
            verify_issuer: Whether to verify the issuer claim
            
        Returns:
            dict: Decoded JWT payload
            
        Raises:
            TokenExpiredError: If token has expired
            InvalidTokenError: If token is invalid
            ScopeValidationError: If required scope is not present
        """
        # First validate the token
        payload = self.validate(token, verify_audience, verify_issuer)
        
        # Convert required_scope to list if it's a string
        if isinstance(required_scope, str):
            required_scopes = [required_scope]
        else:
            required_scopes = required_scope
        
        # Get token scopes (check both 'scope' and 'scp' claims)
        token_scopes = payload.get("scope") or payload.get("scp")
        
        self.logger.debug(f"Checking for required scopes: {required_scopes}")
        self.logger.debug(f"Token scopes: {token_scopes}")
        
        if not token_scopes:
            self.logger.warning(f"Token missing scope claim - required scopes: {required_scopes}")
            raise ScopeValidationError(
                f"Access denied: required scope(s) '{', '.join(required_scopes)}' not found in token (no scope claim present)"
            )
        
        # Parse token scopes - handle both string and array formats
        if isinstance(token_scopes, str):
            scopes_list = token_scopes.split()
        elif isinstance(token_scopes, list):
            scopes_list = token_scopes
        else:
            self.logger.warning(f"Invalid scope format in token: {type(token_scopes)}")
            raise ScopeValidationError(
                f"Access denied: invalid scope format in token - required scope(s) '{', '.join(required_scopes)}'"
            )
        
        self.logger.debug(f"Parsed scopes list: {scopes_list}")
        
        # Check if all required scopes are present
        missing_scopes = [scope for scope in required_scopes if scope not in scopes_list]
        
        if missing_scopes:
            self.logger.warning(f"Required scope(s) {missing_scopes} not present in token scopes: {scopes_list}")
            raise ScopeValidationError(
                f"Access denied: required scope(s) '{', '.join(missing_scopes)}' not present in token. "
                f"Available scopes: {', '.join(scopes_list)}"
            )
        
        self.logger.info(f"Scope validation successful: {required_scopes} found in token")
        return payload
