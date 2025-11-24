from typing import Optional, Dict, Any
from .models import TokenConfig, AuthResult
from .session import SessionManager
from .validator import TokenValidator, TokenValidationError
from .oauth import OAuthClient
from .server import LocalCallbackServer
from urllib.parse import urlparse
from .logger import setup_logger

class AuthSDK:
    def __init__(self, config: TokenConfig, session_manager: Optional[SessionManager] = None):
        self.config = config
        self.session_manager = session_manager or SessionManager()
        self.validator = TokenValidator(config)
        self.oauth_client = OAuthClient(config)
        self.logger = setup_logger(__name__, config.log_level)

    def process_request(self, request_headers: Dict[str, str]) -> AuthResult:
        """
        Process an incoming request.
        Expects 'Authorization' header with 'Bearer <token>'.
        """
        auth_header = request_headers.get("Authorization") or request_headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return AuthResult(is_authenticated=False, error="Missing or invalid Authorization header")

        token_str = auth_header.split(" ")[1]

        try:
            # 1. Validate Incoming JWT
            self.logger.debug(f"Validating incoming JWT")
            if self.config.scope:
                claims = self.validator.validate_with_scope(token_str, self.config.scope)
            else:
                claims = self.validator.validate(token_str)
            jti = claims.get("jti")
            sub = claims.get("sub")
            self.logger.debug(f"Token validated successfully. JTI: {jti}, SUB: {sub}")

            if not jti or not sub:
                self.logger.warning("Token missing required claims (jti or sub)")
                return AuthResult(is_authenticated=False, error="Token missing jti or sub claims")

            # 2. Check Session
            session = self.session_manager.get_session(jti)

            if not session:
                # New Session
                self.logger.info(f"Creating new session for JTI: {jti}")
                session = self.session_manager.create_session(jti, sub)
                # Start OAuth Flow
                auth_url = self.oauth_client.create_authorization_url(session)
                self.session_manager.update_session(session)
                self.logger.info("Initiating OAuth flow for new session")
                return AuthResult(is_authenticated=False, redirect_url=auth_url, session=session)

            # 3. Existing Session
            if session.obo_access_token:
                # Replay protection / Return existing token
                self.logger.info(f"Replay protection: Returning cached token for JTI: {jti}")
                return AuthResult(is_authenticated=True, session=session)
            else:
                # Session exists but no token yet (maybe in progress or failed previously)
                # Restart flow to be safe, or check state? 
                # For simplicity, if no token, we restart flow.
                self.logger.warning(f"Session exists for JTI {jti} but no OBO token, restarting flow")
                auth_url = self.oauth_client.create_authorization_url(session)
                self.session_manager.update_session(session)
                return AuthResult(is_authenticated=False, redirect_url=auth_url, session=session)

        except TokenValidationError as e:
            self.logger.warning(f"Token validation failed: {str(e)}")
            return AuthResult(is_authenticated=False, error=str(e))
        except ValueError as e:
            self.logger.error(f"Validation error: {str(e)}")
            return AuthResult(is_authenticated=False, error=str(e))
        except Exception as e:
            self.logger.error(f"Internal error in process_request: {str(e)}")
            return AuthResult(is_authenticated=False, error=f"Internal error: {str(e)}")

    def handle_callback(self, code: str, state: str) -> AuthResult:
        """
        Handle OAuth2 callback.
        """
        self.logger.debug(f"Handling callback with state: {state}")
        session = self.session_manager.get_session_by_state(state)
        if not session:
            self.logger.error(f"No session found for state: {state}")
            return AuthResult(is_authenticated=False, error="Invalid state or session expired")

        try:
            self.logger.info("Exchanging authorization code for tokens")
            token_response = self.oauth_client.exchange_code_for_token(code, session)
            
            # Update Session
            session.obo_access_token = token_response.get("access_token")
            session.refresh_token = token_response.get("refresh_token")
            session.id_token = token_response.get("id_token")
            self.logger.debug(f"Token exchange successful for session JTI: {session.jti}")
            # Clear PKCE data to prevent reuse if desired, but keeping session active
            session.pkce_verifier = None 
            session.state = None # Clear state to prevent replay of callback
            
            self.session_manager.update_session(session)
            self.logger.info(f"Session updated with OBO tokens for JTI: {session.jti}")
            
            return AuthResult(is_authenticated=True, session=session)
        except Exception as e:
            self.logger.error(f"Token exchange failed: {str(e)}")
            return AuthResult(is_authenticated=False, error=f"Token exchange failed: {str(e)}")
