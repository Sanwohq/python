"""Custom exceptions for the Sanwo SDK."""

from __future__ import annotations


class SanwoError(Exception):
    """Base exception for all Sanwo errors."""


class SanwoConfigurationError(SanwoError):
    """Raised when the Sanwo client is configured with invalid options."""


class SanwoCheckoutError(SanwoError):
    """Raised when checkout parameters are invalid."""
