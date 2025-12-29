"""
AI Shield SDK Exceptions
"""


class AIShieldError(Exception):
    """Base Exception für AI Shield SDK"""
    pass


class APIError(AIShieldError):
    """API Error"""
    pass


class AuthenticationError(AIShieldError):
    """Authentication Error"""
    pass
