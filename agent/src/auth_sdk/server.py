import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Optional, Callable
import logging

class CallbackHandler(BaseHTTPRequestHandler):
    # Class variable to hold reference to SDK instance
    sdk_instance = None
    
    def do_GET(self):
        logger = logging.getLogger(__name__)
        parsed_path = urlparse(self.path)
        query_params = parse_qs(parsed_path.query)

        code = query_params.get('code', [None])[0]
        state = query_params.get('state', [None])[0]
        error = query_params.get('error', [None])[0]

        if code and state:
            logger.info(f"Callback received: code={code[:20]}..., state={state[:20]}...")
            
            # Process callback asynchronously in background thread
            if CallbackHandler.sdk_instance:
                def process_callback():
                    try:
                        result = CallbackHandler.sdk_instance.handle_callback(code, state)
                        logger.info(f"Callback processed successfully: authenticated={result.is_authenticated}")
                    except Exception as e:
                        logger.error(f"Error processing callback: {e}")
                
                import threading
                threading.Thread(target=process_callback, daemon=True).start()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<html><body><h1>Login Successful</h1><p>You can close this window.</p><script>window.close();</script></body></html>")
        elif error:
            logger.warning(f"Callback error received: {error}")
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(f"<html><body><h1>Login Failed</h1><p>{error}</p></body></html>".encode())
        else:
            logger.warning(f"Callback received without code/state: {self.path}")
            self.send_response(404)
            self.end_headers()

class LocalCallbackServer:
    def __init__(self, port: int = 8000, sdk=None):
        self.port = port
        self.sdk = sdk
        self.server: Optional[HTTPServer] = None
        self.thread: Optional[threading.Thread] = None
        self.logger = logging.getLogger(__name__)

    def start(self):
        self.logger.info(f"Starting local callback server on port {self.port}")
        
        # Set SDK reference in handler class
        if self.sdk:
            CallbackHandler.sdk_instance = self.sdk
        
        self.server = HTTPServer(('localhost', self.port), CallbackHandler)
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.daemon = True
        self.thread.start()
        self.logger.info(f"Callback server listening on http://localhost:{self.port}")

    def stop(self):
        if self.server:
            self.logger.info("Stopping callback server")
            CallbackHandler.sdk_instance = None  # Clear SDK reference
            self.server.shutdown()
            self.server.server_close()
            self.server = None

    def wait_for_completion(self, session_jti: str, timeout: int = 300) -> bool:
        """
        Wait for the session to be updated with OBO tokens.
        Returns True if tokens were obtained, False if timeout.
        """
        import time
        start_time = time.time()
        self.logger.debug(f"Waiting for session {session_jti} to be updated (timeout: {timeout}s)")
        
        while time.time() - start_time < timeout:
            if self.sdk and self.sdk.session_manager:
                session = self.sdk.session_manager.get_session(session_jti)
                if session and session.obo_access_token:
                    self.logger.info(f"Session {session_jti} updated with OBO tokens")
                    return True
            time.sleep(0.5)
        
        self.logger.warning(f"Timeout waiting for session {session_jti} to be updated")
        return False
