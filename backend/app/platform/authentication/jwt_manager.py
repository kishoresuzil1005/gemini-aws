import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class JWTManager:
    """
    Handles enterprise-grade JSON Web Token creation, validation, and refresh.
    """
    def __init__(self, secret_key: str = "enterprise_secret", algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm

    def create_access_token(self, subject: str, claims: Dict[str, Any] = None, expires_delta: timedelta = timedelta(minutes=60)) -> str:
        to_encode = {"sub": subject, "exp": datetime.utcnow() + expires_delta}
        if claims:
            to_encode.update(claims)
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except jwt.PyJWTError as e:
            print(f"[JWTManager] Verification failed: {e}")
            return None
