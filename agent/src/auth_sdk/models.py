from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Union
from datetime import datetime

@dataclass
class TokenConfig:
    issuer: str
    audience: str
    jwks_url: str
    authorization_endpoint: str
    token_endpoint: str
    client_id: str
    client_secret: Optional[str] = None
    redirect_uri: str = ""
    scope: str = "openid profile email"
    ssl_verify: Union[bool, str] = True
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

@dataclass
class Session:
    jti: str
    user_id: str
    obo_access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    id_token: Optional[str] = None
    pkce_verifier: Optional[str] = None
    state: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AuthResult:
    is_authenticated: bool
    redirect_url: Optional[str] = None
    session: Optional[Session] = None
    error: Optional[str] = None
