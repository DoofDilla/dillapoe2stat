"""
OAuth 2.1 Authorization Code Flow with PKCE for Path of Exile API

This module implements the complete OAuth flow for Public Clients:
- PKCE (Proof Key for Code Exchange) generation
- Browser-based authorization
- Local callback server on http://127.0.0.1:8080/callback
- Token exchange and refresh
- Secure token storage

Reference: https://www.pathofexile.com/developer/docs/authorization
"""

import secrets
import hashlib
import base64
import webbrowser
import json
import time
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, urlencode
from threading import Thread
import requests

# OAuth endpoints
OAUTH_BASE = "https://www.pathofexile.com"
AUTHORIZE_URL = f"{OAUTH_BASE}/oauth/authorize"
TOKEN_URL = f"{OAUTH_BASE}/oauth/token"

# Client configuration (from your screenshot)
CLIENT_ID = "dillapoe2stat"
CLIENT_SECRET = None  # Public client - no secret
REDIRECT_URI = "http://127.0.0.1:8080/callback"
SCOPES = "account:profile account:characters"

# Token storage
TOKEN_FILE = Path("tokens.json")


class PKCEGenerator:
    """Generate PKCE code verifier and challenge for OAuth flow"""
    
    @staticmethod
    def generate_code_verifier() -> str:
        """Generate a cryptographically random code verifier (43-128 chars)"""
        # Use 32 random bytes = 43 base64url chars (meets RFC 7636 requirements)
        random_bytes = secrets.token_bytes(32)
        return PKCEGenerator._base64url_encode(random_bytes)
    
    @staticmethod
    def generate_code_challenge(verifier: str) -> str:
        """Generate SHA256 code challenge from verifier"""
        # Hash the verifier and encode
        digest = hashlib.sha256(verifier.encode('utf-8')).digest()
        return PKCEGenerator._base64url_encode(digest)
    
    @staticmethod
    def _base64url_encode(data: bytes) -> str:
        """Base64url encoding (RFC 4648 Section 5) - no padding"""
        return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')


class CallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler for OAuth callback"""
    
    # Shared state between handler instances
    auth_code = None
    auth_state = None
    auth_error = None
    
    def do_GET(self):
        """Handle GET request to /callback"""
        # Parse query parameters
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        
        if parsed.path != '/callback':
            self.send_error(404)
            return
        
        # Check for error response
        if 'error' in params:
            CallbackHandler.auth_error = params.get('error', ['Unknown error'])[0]
            error_desc = params.get('error_description', [''])[0]
            
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = f"""
            <html>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1 style="color: red;">❌ Authorization Failed</h1>
                <p><strong>Error:</strong> {CallbackHandler.auth_error}</p>
                <p>{error_desc}</p>
                <p>You can close this window.</p>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
            return
        
        # Success - extract code and state
        CallbackHandler.auth_code = params.get('code', [None])[0]
        CallbackHandler.auth_state = params.get('state', [None])[0]
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        html = """
        <html>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1 style="color: green;">✅ Authorization Successful!</h1>
            <p>You can close this window and return to the application.</p>
            <script>setTimeout(() => window.close(), 3000);</script>
        </body>
        </html>
        """
        self.wfile.write(html.encode())
    
    def log_message(self, format, *args):
        """Suppress HTTP server log messages"""
        pass


class OAuthFlow:
    """Complete OAuth 2.1 Authorization Code Flow with PKCE"""
    
    def __init__(self, client_id: str = CLIENT_ID, redirect_uri: str = REDIRECT_URI, 
                 scopes: str = SCOPES):
        self.client_id = client_id
        self.redirect_uri = redirect_uri
        self.scopes = scopes
        self.code_verifier = None
        self.state = None
    
    def authorize(self) -> dict:
        """
        Start OAuth flow and get access token
        
        Returns:
            dict: Token response with access_token, refresh_token, expires_in, etc.
        
        Raises:
            Exception: If authorization fails
        """
        print("🔐 Starting OAuth 2.1 Authorization Flow...")
        
        # Reset callback handler state
        CallbackHandler.auth_code = None
        CallbackHandler.auth_state = None
        CallbackHandler.auth_error = None
        
        # Step 1: Generate PKCE parameters
        self.code_verifier = PKCEGenerator.generate_code_verifier()
        code_challenge = PKCEGenerator.generate_code_challenge(self.code_verifier)
        self.state = secrets.token_urlsafe(32)
        
        print(f"   Generated PKCE challenge")
        
        # Step 2: Build authorization URL
        auth_params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'scope': self.scopes,
            'state': self.state,
            'redirect_uri': self.redirect_uri,
            'code_challenge': code_challenge,
            'code_challenge_method': 'S256'
        }
        
        auth_url = f"{AUTHORIZE_URL}?{urlencode(auth_params)}"
        
        # Step 3: Start local callback server
        print(f"   Starting callback server on port 8080...")
        server = HTTPServer(('127.0.0.1', 8080), CallbackHandler)
        server_thread = Thread(target=self._run_server, args=(server,), daemon=True)
        server_thread.start()
        
        # Step 4: Open browser for user authorization
        print(f"   Opening browser for authorization...")
        print(f"   Please authorize the application in your browser.")
        webbrowser.open(auth_url)
        
        # Step 5: Wait for callback
        print(f"   Waiting for authorization callback...")
        auth_code = self._wait_for_callback(server, timeout=120)
        
        if not auth_code:
            if CallbackHandler.auth_error:
                raise Exception(f"Authorization failed: {CallbackHandler.auth_error}")
            raise Exception("Authorization timeout - no callback received")
        
        # Verify state
        if CallbackHandler.auth_state != self.state:
            raise Exception("State mismatch - possible CSRF attack")
        
        print(f"   ✅ Authorization code received")
        
        # Step 6: Exchange code for token
        print(f"   Exchanging code for access token...")
        token_data = self._exchange_code_for_token(auth_code)
        
        print(f"   ✅ Access token obtained!")
        print(f"   Token expires in: {token_data.get('expires_in', 0) // 3600} hours")
        
        return token_data
    
    def _run_server(self, server: HTTPServer):
        """Run callback server (in background thread)"""
        try:
            # Keep serving until we get the callback or timeout
            while not CallbackHandler.auth_code and not CallbackHandler.auth_error:
                server.handle_request()
        except Exception as e:
            print(f"   ⚠️  Server error: {e}")
    
    def _wait_for_callback(self, server: HTTPServer, timeout: int = 120) -> str:
        """Wait for authorization callback with timeout"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if CallbackHandler.auth_code:
                return CallbackHandler.auth_code
            if CallbackHandler.auth_error:
                return None
            time.sleep(0.1)  # Check more frequently
        
        return None
    
    def _exchange_code_for_token(self, code: str) -> dict:
        """Exchange authorization code for access token"""
        token_params = {
            'client_id': self.client_id,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri,
            'scope': self.scopes,
            'code_verifier': self.code_verifier
        }
        
        # Public client - no client_secret
        
        response = requests.post(
            TOKEN_URL,
            data=token_params,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': 'DillaPoE2Stat/0.4.0 (+github.com/DoofDilla/dillapoe2stat)'
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"Token exchange failed: {response.status_code} - {response.text}")
        
        return response.json()
    
    def refresh_token(self, refresh_token: str) -> dict:
        """
        Refresh access token using refresh token
        
        Args:
            refresh_token: Valid refresh token
        
        Returns:
            dict: New token response
        """
        print("🔄 Refreshing access token...")
        
        refresh_params = {
            'client_id': self.client_id,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
        
        response = requests.post(
            TOKEN_URL,
            data=refresh_params,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': 'DillaPoE2Stat/0.4.0 (+github.com/DoofDilla/dillapoe2stat)'
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"Token refresh failed: {response.status_code} - {response.text}")
        
        token_data = response.json()
        print(f"   ✅ Token refreshed!")
        
        return token_data


class TokenManager:
    """Manage OAuth tokens - storage, loading, and auto-refresh"""
    
    def __init__(self, token_file: Path = TOKEN_FILE):
        self.token_file = token_file
        self.tokens = None
    
    def save_tokens(self, token_data: dict):
        """Save tokens to file with expiry timestamp"""
        # Add absolute expiry time
        if 'expires_in' in token_data:
            token_data['expires_at'] = time.time() + token_data['expires_in']
        
        with open(self.token_file, 'w') as f:
            json.dump(token_data, f, indent=2)
        
        self.tokens = token_data
        print(f"   💾 Tokens saved to {self.token_file}")
    
    def load_tokens(self) -> dict:
        """Load tokens from file"""
        if not self.token_file.exists():
            return None
        
        try:
            with open(self.token_file, 'r') as f:
                self.tokens = json.load(f)
            return self.tokens
        except Exception as e:
            print(f"⚠️  Failed to load tokens: {e}")
            return None
    
    def get_valid_token(self) -> str:
        """
        Get a valid access token - auto-refresh if needed
        
        Returns:
            str: Valid access token
        
        Raises:
            Exception: If no tokens or refresh fails
        """
        if not self.tokens:
            self.tokens = self.load_tokens()
        
        if not self.tokens:
            raise Exception("No tokens found - please authorize first")
        
        # Check if token is expired (with 5 min buffer)
        expires_at = self.tokens.get('expires_at', 0)
        if time.time() + 300 > expires_at:  # 5 min buffer
            print("⏰ Access token expired - refreshing...")
            
            # Refresh token
            refresh_token = self.tokens.get('refresh_token')
            if not refresh_token:
                raise Exception("No refresh token available - please re-authorize")
            
            flow = OAuthFlow()
            new_tokens = flow.refresh_token(refresh_token)
            self.save_tokens(new_tokens)
        
        return self.tokens['access_token']
    
    def clear_tokens(self):
        """Clear stored tokens"""
        if self.token_file.exists():
            self.token_file.unlink()
            print("   🗑️  Tokens cleared")
        self.tokens = None


def get_access_token() -> str:
    """
    Convenience function: Get valid access token (auto-authorize if needed)
    
    Returns:
        str: Valid access token
    """
    manager = TokenManager()
    
    try:
        return manager.get_valid_token()
    except Exception as e:
        print(f"⚠️  {e}")
        print("   Starting new authorization flow...")
        
        # Start OAuth flow
        flow = OAuthFlow()
        tokens = flow.authorize()
        manager.save_tokens(tokens)
        
        return tokens['access_token']


if __name__ == "__main__":
    # Test the OAuth flow
    print("=" * 60)
    print("Testing OAuth 2.1 Flow with PKCE")
    print("=" * 60)
    
    try:
        token = get_access_token()
        print("\n✅ SUCCESS!")
        print(f"Access Token: {token[:20]}...")
        
        # Test API call
        print("\nTesting API call...")
        response = requests.get(
            "https://www.pathofexile.com/api/profile",
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if response.status_code == 200:
            profile = response.json()
            print(f"   ✅ Profile loaded: {profile.get('name', 'Unknown')}")
        else:
            print(f"   ⚠️  API call failed: {response.status_code}")
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
