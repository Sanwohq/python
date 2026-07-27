"""Read Sanwo configuration from Django settings.

Provides a thin helper that reads ``SANWO_*`` settings from
``django.conf.settings`` and returns a :class:`~sanwo.client.Sanwo` instance
(lazily cached per-process).
"""

from __future__ import annotations

from typing import Optional

from sanwo.client import Sanwo

_client: Optional[Sanwo] = None


def get_sanwo_client() -> Sanwo:
    """Return a lazily-initialised :class:`Sanwo` client.

    Configuration is read from ``django.conf.settings`` each time the client
    is first created (i.e. after ``django.setup()`` has been called).

    Settings
    --------
    ``SANWO_PROVIDER`` : str
        Payment provider id (default ``"paystack"``).
    ``SANWO_PUBLIC_KEY`` : str
        Provider public/publishable key (required).
    ``SANWO_CURRENCY`` : str
        ISO 4217 currency code (default ``"NGN"``).
    ``SANWO_DEBUG`` : bool
        Enable debug logging in the browser console (default ``False``).
    """
    global _client  # noqa: PLW0603
    if _client is None:
        from django.conf import settings

        _client = Sanwo(
            provider=getattr(settings, "SANWO_PROVIDER", "paystack"),
            public_key=getattr(settings, "SANWO_PUBLIC_KEY", ""),
            currency=getattr(settings, "SANWO_CURRENCY", "NGN"),
            debug=getattr(settings, "SANWO_DEBUG", False),
            template_url=getattr(settings, "SANWO_TEMPLATE_URL", None),
            template=getattr(settings, "SANWO_TEMPLATE", None),
        )
    return _client


def reset_client() -> None:
    """Reset the cached client (useful in tests)."""
    global _client  # noqa: PLW0603
    _client = None
