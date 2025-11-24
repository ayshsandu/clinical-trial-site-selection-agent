"""
Agent OAuth Provider for special agent authentication flows.

This module provides OAuth authentication specifically for agent identities,
where the agent authenticates itself (not on behalf of a user) to obtain
tokens for accessing downstream services.
"""

import os
import time
import secrets
import hashlib
import base64
import requests
from typing import Optional, Dict, Any
from .logger import setup_logger


class AgentOAuthProvider:
    """
    OAuth provider for agent authentication flow.
    
    This class handles the special agent authentication flow where the agent
    authenticates itself to obtain tokens for making requests to downstream services.
    
    The flow is:
    1. Initiate authorization with PKCE
    2. Authenticate with agent credentials
    3. Exchange code for tokens
    """
    
    def __init__(
        self,
        client_id: str,
        client_secret: Optional[str] = None,
        redirect_url: str = None,
        agent_id: str = None,
        agent_password: str = None,
        token_endpoint: str = None,
        ssl_verify: bool = True,
        log_level: str = "INFO"
    ):
        """
        Initialize the Agent OAuth Provider.
        
        Args:
            client_id: OAuth client ID
            client_secret: OAuth client secret (optional)
            redirect_url: OAuth redirect URL (default: http://localhost/callback)
            agent_id: Agent identifier for authentication
            agent_password: Agent password for authentication
            token_endpoint: OAuth token endpoint URL
            ssl_verify: Whether to verify SSL certificates (default: True)
            log_level: Logging level (default: INFO)
            
        Raises:
            ValueError: If required parameters are missing
        """
        if not (client_id and agent_id and agent_password):
            raise ValueError("client_id, agent_id, and agent_password are required")
        
        self._client_id = client_id
        self._client_secret = client_secret
        self._redirect_url = redirect_url or "http://localhost/callback"
        self._agent_id = agent_id
        self._agent_password = agent_password
        self._token_endpoint = token_endpoint
        self._ssl_verify = ssl_verify
        self._code_verifier = self._generate_code_verifier()
        self._code_challenge = self._generate_code_challenge(self._code_verifier)
        self._logger = setup_logger(__name__, log_level)
    
    def _generate_code_verifier(self) -> str:
        """Generate a random code verifier for PKCE."""
        return secrets.token_urlsafe(32)
    
    def _generate_code_challenge(self, verifier: str) -> str:
        """Generate code challenge from verifier using S256."""
        sha256 = hashlib.sha256(verifier.encode()).digest()
        return base64.urlsafe_b64encode(sha256).decode().rstrip('=')
    
    def _get_token_endpoint(self) -> str:
        """Get the token endpoint URL."""
        return self._token_endpoint
    
    def acquire_agent_tokens(self) -> Dict[str, Any]:
        """
        Acquire tokens using the special agent authentication flow.
        
        Returns:
            dict: OAuth tokens containing:
                - access_token: The access token
                - token_type: Token type (usually "Bearer")
                - expires_in: Token expiration time in seconds
                - refresh_token: Refresh token (if available)
                - scope: Token scope
                - obtained_at: Timestamp when token was obtained (milliseconds)
                
        Raises:
            Exception: If any step of the authentication flow fails
        """
        try:
            self._logger.info('AgentOAuthProvider: Starting agent authentication flow')
            
            # Step 1: Initiate authorization with direct response mode
            auth_response = self._initiate_agent_authorization()
            self._logger.info(f'AgentOAuthProvider: Authorization initiated, flowId: {auth_response["flowId"]}')
            
            # Step 2: Authenticate with agent credentials
            code_response = self._authenticate_agent(auth_response['flowId'])
            self._logger.info('AgentOAuthProvider: Agent authentication successful, received authorization code')
            
            # Step 3: Exchange code for tokens
            tokens = self._exchange_agent_code_for_tokens(code_response['authData']['code'])
            self._logger.info('AgentOAuthProvider: Token exchange completed successfully')
            
            return tokens
        except Exception as error:
            self._logger.error(f'AgentOAuthProvider: Agent authentication failed: {error}')
            raise error
    
    def _initiate_agent_authorization(self) -> Dict[str, Any]:
        """
        Step 1: Initiate authorization request with direct response mode.
        
        Returns:
            dict: Authorization response containing flowId
            
        Raises:
            Exception: If authorization initiation fails
        """
        token_endpoint = self._get_token_endpoint()
        base_url = token_endpoint.replace('/oauth2/token', '')
        auth_url = f"{base_url}/oauth2/authorize"
        
        self._logger.info(f'AgentOAuthProvider: Initiating authorization request to {auth_url}')
        body = {
            'client_id': self._client_id,
            'response_type': 'code',
            'redirect_uri': self._redirect_url,
            'scope': 'openid',
            'response_mode': 'direct',
            'code_challenge': self._code_challenge,
            'code_challenge_method': 'S256'
        }
        
        response = requests.post(auth_url, data=body, headers={
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }, verify=self._ssl_verify)
        
        if not response.ok:
            raise Exception(f"Authorization initiation failed: {response.status_code} {response.reason}")
        
        auth_data = response.json()
        self._logger.info(f'AgentOAuthProvider: Authorization initiated: {auth_data}')
        return auth_data
    
    def _authenticate_agent(self, flow_id: str) -> Dict[str, Any]:
        """
        Step 2: Authenticate with agent credentials.
        
        Args:
            flow_id: Flow ID from authorization initiation
            
        Returns:
            dict: Authentication response containing authorization code
            
        Raises:
            Exception: If agent authentication fails
        """
        token_endpoint = self._get_token_endpoint()
        base_url = token_endpoint.replace('/oauth2/token', '')
        authn_url = f"{base_url}/oauth2/authn"
        
        body = {
            'flowId': flow_id,
            'selectedAuthenticator': {
                'authenticatorId': "QmFzaWNBdXRoZW50aWNhdG9yOkxPQ0FM",  # Basic Authenticator ID
                'params': {
                    'username': f"AGENT/{self._agent_id or self._client_id}",
                    'password': self._agent_password or self._client_secret,
                }
            }
        }
        
        response = requests.post(authn_url, json=body, headers={
            'Content-Type': 'application/json',
        }, verify=self._ssl_verify)
        
        if not response.ok:
            raise Exception(f"Agent authentication failed: {response.status_code} {response.reason}")
        
        authn_data = response.json()
        return authn_data
    
    def _exchange_agent_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """
        Step 3: Exchange authorization code for tokens.
        
        Args:
            code: Authorization code from authentication
            
        Returns:
            dict: Token response containing access_token, refresh_token, etc.
            
        Raises:
            Exception: If token exchange fails
        """
        token_endpoint = self._token_endpoint
        
        body = {
            'grant_type': 'authorization_code',
            'client_id': self._client_id,
            'code': code,
            'code_verifier': self._code_verifier,
            'redirect_uri': self._redirect_url,
        }
        
        response = requests.post(token_endpoint, data=body, headers={
            'Content-Type': 'application/x-www-form-urlencoded',
        }, verify=self._ssl_verify)
        
        if not response.ok:
            raise Exception(f"Token exchange failed: {response.status_code} {response.reason}")
        
        token_data = response.json()
        
        tokens = {
            'access_token': token_data['access_token'],
            'token_type': token_data.get('token_type', 'Bearer'),
            'expires_in': token_data.get('expires_in'),
            'refresh_token': token_data.get('refresh_token'),
            'scope': token_data.get('scope'),
        }
        
        # Store obtained time for token expiry calculation
        tokens['obtained_at'] = int(time.time() * 1000)
        
        return tokens
