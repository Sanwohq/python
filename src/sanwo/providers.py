"""Provider definitions for the Sanwo SDK.

Each constant represents a supported payment provider with its metadata.
You can pass either the constant or the string ID (e.g. ``"paystack"``)
when initialising a :class:`~sanwo.client.Sanwo` instance.
"""

from __future__ import annotations

from sanwo.types import ProviderConfig

PAYSTACK = ProviderConfig(
    id="paystack",
    name="Paystack",
    display_name="Paystack",
    website="https://paystack.com",
    sdk_type="popup",
)

FLUTTERWAVE = ProviderConfig(
    id="flutterwave",
    name="Flutterwave",
    display_name="Flutterwave",
    website="https://flutterwave.com",
    sdk_type="popup",
)

RAZORPAY = ProviderConfig(
    id="razorpay",
    name="Razorpay",
    display_name="Razorpay",
    website="https://razorpay.com",
    sdk_type="popup",
)

MONNIFY = ProviderConfig(
    id="monnify",
    name="Monnify",
    display_name="Monnify",
    website="https://monnify.com",
    sdk_type="popup",
)

INTERSWITCH = ProviderConfig(
    id="interswitch",
    name="Interswitch",
    display_name="Interswitch",
    website="https://interswitchgroup.com",
    sdk_type="redirect",
)

# Lookup table for resolving string IDs to ProviderConfig instances.
_PROVIDERS = {
    "paystack": PAYSTACK,
    "flutterwave": FLUTTERWAVE,
    "razorpay": RAZORPAY,
    "monnify": MONNIFY,
    "interswitch": INTERSWITCH,
}


def resolve_provider(provider: str | ProviderConfig) -> ProviderConfig:
    """Resolve a provider string or ``ProviderConfig`` to a ``ProviderConfig``.

    Parameters
    ----------
    provider:
        Either a :class:`ProviderConfig` instance or a string ID such as
        ``"paystack"``.

    Returns
    -------
    ProviderConfig
        The resolved provider configuration.

    Raises
    ------
    ValueError
        If *provider* is a string that does not match any known provider.
    """
    if isinstance(provider, ProviderConfig):
        return provider
    key = provider.lower().strip()
    if key not in _PROVIDERS:
        valid = ", ".join(sorted(_PROVIDERS))
        raise ValueError(
            f"Unknown provider {provider!r}. Valid providers: {valid}"
        )
    return _PROVIDERS[key]
