"""Sanwo Flask integration.

Usage::

    from flask import Flask
    from sanwo.flask import SanwoFlask

    app = Flask(__name__)
    app.config['SANWO_PROVIDER'] = 'paystack'
    app.config['SANWO_PUBLIC_KEY'] = 'pk_test_xxx'

    sanwo = SanwoFlask(app)
    # or: sanwo = SanwoFlask(); sanwo.init_app(app)

In Jinja2 templates::

    {{ sanwo_scripts() }}
    {{ sanwo_checkout(amount=500000, email="user@example.com") }}
    {{ sanwo_custom_amount(email="user@example.com") }}
"""

def __getattr__(name: str):  # type: ignore[misc]
    if name == "SanwoFlask":
        from sanwo.flask.extension import SanwoFlask

        return SanwoFlask
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["SanwoFlask"]
