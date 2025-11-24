"""
Agent OAuth Provider for special agent authentication flows.

This module provides OAuth authentication specifically for agent identities,
where the agent authenticates itself (not on behalf of a user) to obtain
tokens for accessing downstream services.
"""

import asyncio
import time
from typing import Optional, Dict, Any
from asgardeo import AsgardeoConfig
from asgardeo_ai import AgentAuthManager, AgentConfig
from .logger import setup_logger





class AgentOAuthProvider:
    """
    OAuth provider for agent authentication flow using asgardeo-ai SDK.
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
        """
        if not (client_id and agent_id and agent_password):
            raise ValueError("client_id, agent_id, and agent_password are required")
        
        self._logger = setup_logger(__name__, log_level)
        
        # Derive base_url from token_endpoint if possible
        base_url = None
        if token_endpoint:
            if "/oauth2/token" in token_endpoint:
                base_url = token_endpoint.split("/oauth2/token")[0]
            else:
                base_url = token_endpoint
        
        if not base_url:
             raise ValueError("Could not derive base_url from token_endpoint")

        self.asgardeo_config = AsgardeoConfig(
            base_url=base_url,
            client_id=client_id,
            client_secret=client_secret or "",
            redirect_uri=redirect_url or "http://localhost/callback"
        )
        
        self.agent_config = AgentConfig(
            agent_id=agent_id,
            agent_secret=agent_password
        )
        
        self._ssl_verify = ssl_verify

    async def acquire_agent_tokens(self) -> Dict[str, Any]:
        """
        Acquire tokens using the agent authentication flow.
        """
        try:
            self._logger.info('AgentOAuthProvider: Starting agent authentication flow')
            
            # Use AgentAuthManager to get tokens
            # Note: ssl_verify is not directly supported by AsgardeoConfig yet, 
            # assuming the library handles it or environment settings apply.
            async with AgentAuthManager(self.asgardeo_config, self.agent_config) as auth_manager:
                token = await auth_manager.get_agent_token()
                
                self._logger.info('AgentOAuthProvider: Token exchange completed successfully')
                
                return {
                    "access_token": token.access_token,
                    "token_type": "Bearer",
                    "expires_in": token.expires_in,
                    "refresh_token": token.refresh_token,
                    "scope": token.scope,
                    "obtained_at": int(time.time() * 1000)
                }
                
        except Exception as error:
            self._logger.error(f'AgentOAuthProvider: Agent authentication failed: {error}')
            raise error
