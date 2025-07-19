"""
Secure secrets management system.

This module provides a secure way to manage secrets using multiple backends
including AWS Secrets Manager, HashiCorp Vault, and environment variables
with proper encryption and rotation capabilities.
"""

import os
import json
import base64
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import boto3
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)


class SecretProvider(str, Enum):
    """Supported secret providers."""
    ENV = "environment"
    AWS_SECRETS_MANAGER = "aws_secrets_manager"
    HASHICORP_VAULT = "hashicorp_vault"
    LOCAL_ENCRYPTED = "local_encrypted"


@dataclass
class Secret:
    """Secret data model."""
    key: str
    value: str
    version: Optional[str] = None
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class SecretBackend(ABC):
    """Abstract base class for secret backends."""
    
    @abstractmethod
    async def get_secret(self, key: str) -> Optional[Secret]:
        """Retrieve a secret by key."""
        pass
    
    @abstractmethod
    async def set_secret(self, key: str, value: str, metadata: Optional[Dict] = None) -> bool:
        """Store a secret."""
        pass
    
    @abstractmethod
    async def delete_secret(self, key: str) -> bool:
        """Delete a secret."""
        pass
    
    @abstractmethod
    async def list_secrets(self) -> List[str]:
        """List all available secret keys."""
        pass
    
    @abstractmethod
    async def rotate_secret(self, key: str) -> Optional[Secret]:
        """Rotate a secret."""
        pass


class EnvironmentSecretBackend(SecretBackend):
    """Environment variable secret backend with encryption support."""
    
    def __init__(self, encryption_key: Optional[str] = None):
        """
        Initialize environment backend.
        
        Args:
            encryption_key: Optional key for encrypting values in memory
        """
        self._cache: Dict[str, Secret] = {}
        self._fernet = None
        
        if encryption_key:
            # Use provided key or generate from master password
            key = base64.urlsafe_b64encode(
                PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=b'ngx-voice-agent-salt',
                    iterations=100000,
                ).derive(encryption_key.encode())
            )
            self._fernet = Fernet(key)
    
    async def get_secret(self, key: str) -> Optional[Secret]:
        """Get secret from environment variables."""
        # Check cache first
        if key in self._cache:
            return self._cache[key]
        
        # Get from environment
        value = os.getenv(key)
        if not value:
            return None
        
        # Decrypt if encryption is enabled
        if self._fernet and value.startswith("encrypted:"):
            try:
                encrypted_data = value[10:]  # Remove "encrypted:" prefix
                value = self._fernet.decrypt(base64.b64decode(encrypted_data)).decode()
            except Exception as e:
                logger.error(f"Failed to decrypt secret {key}: {e}")
                return None
        
        secret = Secret(
            key=key,
            value=value,
            created_at=datetime.utcnow()
        )
        
        # Cache the secret
        self._cache[key] = secret
        return secret
    
    async def set_secret(self, key: str, value: str, metadata: Optional[Dict] = None) -> bool:
        """Set secret in environment (only in memory, not persistent)."""
        # Encrypt if enabled
        if self._fernet:
            encrypted = base64.b64encode(
                self._fernet.encrypt(value.encode())
            ).decode()
            value = f"encrypted:{encrypted}"
        
        os.environ[key] = value
        self._cache[key] = Secret(
            key=key,
            value=value,
            created_at=datetime.utcnow(),
            metadata=metadata
        )
        return True
    
    async def delete_secret(self, key: str) -> bool:
        """Delete secret from environment."""
        if key in os.environ:
            del os.environ[key]
        if key in self._cache:
            del self._cache[key]
        return True
    
    async def list_secrets(self) -> List[str]:
        """List all environment variables that look like secrets."""
        secret_patterns = [
            "_KEY", "_SECRET", "_TOKEN", "_PASSWORD", "_PASS",
            "_API", "_CREDENTIAL", "_AUTH"
        ]
        
        secrets = []
        for key in os.environ:
            if any(pattern in key.upper() for pattern in secret_patterns):
                secrets.append(key)
        
        return secrets
    
    async def rotate_secret(self, key: str) -> Optional[Secret]:
        """Environment variables don't support rotation."""
        logger.warning(f"Secret rotation not supported for environment backend: {key}")
        return None


class AWSSecretsManagerBackend(SecretBackend):
    """AWS Secrets Manager backend."""
    
    def __init__(self, region_name: str = "us-east-1", endpoint_url: Optional[str] = None):
        """
        Initialize AWS Secrets Manager backend.
        
        Args:
            region_name: AWS region
            endpoint_url: Optional endpoint URL for testing
        """
        self._client = boto3.client(
            'secretsmanager',
            region_name=region_name,
            endpoint_url=endpoint_url
        )
        self._cache: Dict[str, Secret] = {}
        self._cache_ttl = timedelta(minutes=5)
    
    async def get_secret(self, key: str) -> Optional[Secret]:
        """Get secret from AWS Secrets Manager."""
        # Check cache
        if key in self._cache:
            cached_secret = self._cache[key]
            if cached_secret.created_at and \
               datetime.utcnow() - cached_secret.created_at < self._cache_ttl:
                return cached_secret
        
        try:
            response = self._client.get_secret_value(SecretId=key)
            
            # Parse secret value
            if 'SecretString' in response:
                secret_value = response['SecretString']
                # Try to parse as JSON
                try:
                    secret_data = json.loads(secret_value)
                    # If it's a dict with a 'value' key, use that
                    if isinstance(secret_data, dict) and 'value' in secret_data:
                        secret_value = secret_data['value']
                except json.JSONDecodeError:
                    # Use as-is if not JSON
                    pass
            else:
                # Binary secret
                secret_value = base64.b64decode(response['SecretBinary']).decode()
            
            secret = Secret(
                key=key,
                value=secret_value,
                version=response.get('VersionId'),
                created_at=datetime.utcnow(),
                metadata={
                    'ARN': response.get('ARN'),
                    'Name': response.get('Name'),
                    'VersionStages': response.get('VersionStages', [])
                }
            )
            
            # Cache the secret
            self._cache[key] = secret
            return secret
            
        except self._client.exceptions.ResourceNotFoundException:
            logger.warning(f"Secret not found in AWS: {key}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving secret from AWS: {e}")
            return None
    
    async def set_secret(self, key: str, value: str, metadata: Optional[Dict] = None) -> bool:
        """Create or update secret in AWS Secrets Manager."""
        try:
            # Try to update existing secret
            try:
                self._client.update_secret(
                    SecretId=key,
                    SecretString=value
                )
            except self._client.exceptions.ResourceNotFoundException:
                # Create new secret
                self._client.create_secret(
                    Name=key,
                    SecretString=value,
                    Tags=[
                        {'Key': 'ManagedBy', 'Value': 'NGXVoiceAgent'},
                        {'Key': 'Environment', 'Value': os.getenv('ENVIRONMENT', 'development')}
                    ]
                )
            
            # Invalidate cache
            if key in self._cache:
                del self._cache[key]
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting secret in AWS: {e}")
            return False
    
    async def delete_secret(self, key: str) -> bool:
        """Delete secret from AWS Secrets Manager."""
        try:
            self._client.delete_secret(
                SecretId=key,
                ForceDeleteWithoutRecovery=False  # Safe delete with recovery window
            )
            
            # Remove from cache
            if key in self._cache:
                del self._cache[key]
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting secret from AWS: {e}")
            return False
    
    async def list_secrets(self) -> List[str]:
        """List all secrets in AWS Secrets Manager."""
        secrets = []
        
        try:
            paginator = self._client.get_paginator('list_secrets')
            
            for page in paginator.paginate():
                for secret in page['SecretList']:
                    secrets.append(secret['Name'])
            
            return secrets
            
        except Exception as e:
            logger.error(f"Error listing secrets from AWS: {e}")
            return []
    
    async def rotate_secret(self, key: str) -> Optional[Secret]:
        """Initiate secret rotation in AWS."""
        try:
            # Start rotation
            self._client.rotate_secret(
                SecretId=key,
                RotationRules={
                    'AutomaticallyAfterDays': 30
                }
            )
            
            # Get the new version
            return await self.get_secret(key)
            
        except Exception as e:
            logger.error(f"Error rotating secret in AWS: {e}")
            return None


class SecretsManager:
    """
    Main secrets manager that handles multiple backends and provides
    a unified interface for secret management.
    """
    
    def __init__(self, default_provider: SecretProvider = SecretProvider.ENV):
        """
        Initialize secrets manager.
        
        Args:
            default_provider: Default secret provider to use
        """
        self._backends: Dict[SecretProvider, SecretBackend] = {}
        self._default_provider = default_provider
        self._required_secrets: List[str] = []
        
        # Initialize backends based on configuration
        self._initialize_backends()
    
    def _initialize_backends(self):
        """Initialize configured secret backends."""
        # Always initialize environment backend
        encryption_key = os.getenv("SECRETS_ENCRYPTION_KEY")
        self._backends[SecretProvider.ENV] = EnvironmentSecretBackend(encryption_key)
        
        # Initialize AWS backend if configured
        if os.getenv("AWS_SECRETS_ENABLED", "false").lower() == "true":
            self._backends[SecretProvider.AWS_SECRETS_MANAGER] = AWSSecretsManagerBackend(
                region_name=os.getenv("AWS_REGION", "us-east-1")
            )
        
        # Add more backends as needed (Vault, etc.)
    
    async def get_secret(
        self, 
        key: str, 
        provider: Optional[SecretProvider] = None,
        required: bool = True
    ) -> Optional[str]:
        """
        Get a secret value.
        
        Args:
            key: Secret key
            provider: Specific provider to use (uses default if None)
            required: Whether this secret is required (logs warning if missing)
            
        Returns:
            Secret value or None if not found
        """
        provider = provider or self._default_provider
        
        # Try specified provider first
        if provider in self._backends:
            secret = await self._backends[provider].get_secret(key)
            if secret:
                return secret.value
        
        # Fallback to other providers
        for p, backend in self._backends.items():
            if p != provider:
                secret = await backend.get_secret(key)
                if secret:
                    logger.info(f"Secret {key} found in fallback provider {p}")
                    return secret.value
        
        # Log warning for required secrets
        if required:
            logger.warning(f"Required secret not found: {key}")
        
        return None
    
    async def get_secrets(self, keys: List[str]) -> Dict[str, Optional[str]]:
        """Get multiple secrets at once."""
        results = {}
        for key in keys:
            results[key] = await self.get_secret(key)
        return results
    
    async def set_secret(
        self, 
        key: str, 
        value: str,
        provider: Optional[SecretProvider] = None,
        metadata: Optional[Dict] = None
    ) -> bool:
        """Set a secret value."""
        provider = provider or self._default_provider
        
        if provider not in self._backends:
            logger.error(f"Provider not available: {provider}")
            return False
        
        return await self._backends[provider].set_secret(key, value, metadata)
    
    async def validate_required_secrets(self, required_keys: List[str]) -> Dict[str, bool]:
        """
        Validate that all required secrets are available.
        
        Args:
            required_keys: List of required secret keys
            
        Returns:
            Dict mapping keys to availability status
        """
        results = {}
        missing = []
        
        for key in required_keys:
            secret = await self.get_secret(key, required=False)
            results[key] = secret is not None
            if not secret:
                missing.append(key)
        
        if missing:
            logger.error(f"Missing required secrets: {', '.join(missing)}")
        
        return results
    
    async def rotate_secrets(self, keys: Optional[List[str]] = None) -> Dict[str, bool]:
        """
        Rotate specified secrets or all secrets.
        
        Args:
            keys: Specific keys to rotate (None for all)
            
        Returns:
            Dict mapping keys to rotation success status
        """
        results = {}
        
        # Get keys to rotate
        if not keys:
            keys = []
            for backend in self._backends.values():
                keys.extend(await backend.list_secrets())
        
        # Rotate each key
        for key in keys:
            success = False
            for backend in self._backends.values():
                secret = await backend.rotate_secret(key)
                if secret:
                    success = True
                    break
            results[key] = success
        
        return results
    
    def get_safe_config(self) -> Dict[str, Any]:
        """
        Get configuration with secrets masked.
        
        Returns:
            Configuration dict with secret values replaced with "***"
        """
        config = {}
        
        # List of configuration keys to include
        config_keys = [
            "ENVIRONMENT",
            "LOG_LEVEL",
            "API_VERSION",
            "RATE_LIMIT_PER_MINUTE",
            "ALLOWED_ORIGINS"
        ]
        
        # Add non-secret configuration
        for key in config_keys:
            value = os.getenv(key)
            if value:
                config[key] = value
        
        # Add masked secrets
        secret_keys = [
            "OPENAI_API_KEY",
            "ELEVENLABS_API_KEY",
            "SUPABASE_URL",
            "JWT_SECRET"
        ]
        
        for key in secret_keys:
            if os.getenv(key):
                config[key] = "***configured***"
            else:
                config[key] = "***missing***"
        
        return config


# Global instance
secrets_manager = SecretsManager()


# Helper functions for backward compatibility
async def get_secret(key: str, required: bool = True) -> Optional[str]:
    """Get a secret value."""
    return await secrets_manager.get_secret(key, required=required)


async def validate_secrets() -> bool:
    """Validate all required secrets are present."""
    required = [
        "OPENAI_API_KEY",
        "ELEVENLABS_API_KEY", 
        "SUPABASE_URL",
        "SUPABASE_ANON_KEY",
        "JWT_SECRET"
    ]
    
    results = await secrets_manager.validate_required_secrets(required)
    return all(results.values())