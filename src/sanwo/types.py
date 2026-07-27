"""Type definitions for the Sanwo SDK."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class ProviderConfig:
    """Describes a supported payment provider."""

    id: str
    name: str
    display_name: str
    website: str
    sdk_type: str  # "inline" | "popup" | "redirect" | "embedded"


@dataclass
class CheckoutCustomer:
    """Customer information for a checkout."""

    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None


@dataclass
class CheckoutOptions:
    """Options passed to render a checkout."""

    amount: int
    email: str
    currency: Optional[str] = None
    reference: Optional[str] = None
    description: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    button_text: str = "Pay Now"
    button_class: str = "sanwo-button"
    callback: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)


@dataclass
class SanwoConfig:
    """Configuration for a Sanwo client instance."""

    provider: str
    public_key: str
    currency: str = "NGN"
    debug: bool = False
    script_url: str = (
        "https://cdn.jsdelivr.net/npm/@sanwohq/embed/dist/sanwo.global.js"
    )
