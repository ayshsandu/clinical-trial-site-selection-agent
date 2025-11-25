import secrets
import hashlib
import base64
import requests
from urllib.parse import urlencode
from typing import Optional
from .models import TokenConfig, Session
from .agent_auth import AgentOAuthProvider
from .logger import setup_logger

def generate_code_verifier() -> str:
    """Generate a random code verifier for PKCE."""
    return secrets.token_urlsafe(64)

def generate_code_challenge(verifier: str) -> str:
    """Generate code challenge from verifier using S256."""
    digest = hashlib.sha256(verifier.encode()).digest()
    return base64.urlsafe_b64encode(digest).decode().rstrip("=")

class OAuthClient:
    def __init__(self, config: TokenConfig):
        self.config = config
        self.logger = setup_logger(__name__, config.log_level)

    def _generate_pkce_pair(self) -> tuple[str, str]:
        verifier = generate_code_verifier()
        challenge = generate_code_challenge(verifier)
        return verifier, challenge

    def create_authorization_url(self, session: Session, agent_auth_provider: Optional[AgentOAuthProvider] = None) -> str:
        """
        Create authorization URL for OAuth flow.
        
        Args:
            session: The session object to store PKCE and state
            agent_auth_provider: Optional AgentOAuthProvider for agent authentication
            
        Returns:
            str: The authorization URL
        """

        # Standard OAuth flow with PKCE
        verifier, challenge = self._generate_pkce_pair()
        session.pkce_verifier = verifier
        
        state = secrets.token_urlsafe(32)
        session.state = state

        params = {
            "client_id": self.config.client_id,
            "response_type": "code",
            "redirect_uri": self.config.redirect_uri,
            "scope": self.config.scope,
            "state": state,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
        }
        
        #if agent_auth_provider add additional 'requested_actor' param
        if agent_auth_provider:
            params["requested_actor"] = agent_auth_provider._agent_id

        self.logger.debug(f"Generated authorization URL with state: {state}")
        
        return f"{self.config.authorization_endpoint}?{urlencode(params)}"

    def exchange_code_for_token(self, code: str, session: Session, agent_token: Optional[str] = None) -> dict:
        if not session.pkce_verifier:
            raise ValueError("No PKCE verifier found in session")

        data = {
            "grant_type": "authorization_code",
            "client_id": self.config.client_id,
            "code": code,
            "redirect_uri": self.config.redirect_uri,
            "code_verifier": session.pkce_verifier,
        }

        if agent_token:
            self.logger.debug("Agent access token provided")

            data["actor_token"] = agent_token

        self.logger.debug("Preparing to exchange code for token with data: {}".format({k: v for k, v in data.items() if k != "code_verifier"}))
       
        try:
            self.logger.info(f"Exchanging authorization code for tokens at {self.config.token_endpoint}")
            response = requests.post(self.config.token_endpoint, data=data, verify=self.config.ssl_verify)
            response.raise_for_status()
            self.logger.debug("Token exchange successful")
            return response.json()
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Token exchange request failed: {e.response.status_code if e.response else 'No response'} - {e.response.text if e.response else str(e)}")
            if e.response is not None:
                raise ValueError(f"Token exchange failed: {e.response.status_code} {e.response.text}")
            raise ValueError(f"Token exchange failed: {str(e)}")
