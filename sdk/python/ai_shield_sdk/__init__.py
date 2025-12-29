"""
AI Shield SDK - Python SDK für AI Shield Agents API

Einfache Integration der AI Shield Agents API in Python-Projekte.
"""

from .client import AIShieldClient
from .exceptions import AIShieldError, APIError, AuthenticationError

__version__ = "1.0.0"
__all__ = ["AIShieldClient", "AIShieldError", "APIError", "AuthenticationError"]
