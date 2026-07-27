"""Sanwo FastAPI integration.

Usage::

    from fastapi import FastAPI
    from sanwo.fastapi import SanwoFastAPI

    app = FastAPI()
    sanwo = SanwoFastAPI(app, provider="paystack", public_key="pk_test_xxx")

In Jinja2 templates::

    {{ sanwo_scripts() }}
    {{ sanwo_checkout(amount=500000, email="user@example.com") }}
    {{ sanwo_custom_amount(email="user@example.com") }}
"""

def __getattr__(name: str):  # type: ignore[misc]
    if name == "SanwoFastAPI":
        from sanwo.fastapi.extension import SanwoFastAPI

        return SanwoFastAPI
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["SanwoFastAPI"]
