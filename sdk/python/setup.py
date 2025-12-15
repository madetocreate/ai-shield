"""
Setup für AI Shield Python SDK
"""

from setuptools import setup, find_packages

setup(
    name="ai-shield-sdk",
    version="1.0.0",
    description="Python SDK für AI Shield Agents API",
    author="AI Shield",
    packages=find_packages(),
    install_requires=[
        "httpx>=0.25.0",
    ],
    python_requires=">=3.8",
)
