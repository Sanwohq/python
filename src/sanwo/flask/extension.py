"""Flask extension for Sanwo payments."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from flask import Flask

from sanwo.client import Sanwo
from sanwo.flask.helpers import (
    sanwo_checkout,
    sanwo_custom_amount,
    sanwo_scripts,
)


class SanwoFlask:
    """Flask extension that provides Sanwo payment helpers.

    Can be initialised immediately or deferred with
    :meth:`init_app`::

        # Immediate
        sanwo = SanwoFlask(app)

        # Deferred (application factory pattern)
        sanwo = SanwoFlask()
        sanwo.init_app(app)

    Configuration is read from ``app.config``:

    ``SANWO_PROVIDER``
        Payment provider id (default ``"paystack"``).
    ``SANWO_PUBLIC_KEY``
        Provider public/publishable key (**required**).
    ``SANWO_CURRENCY``
        ISO 4217 currency code (default ``"NGN"``).
    ``SANWO_DEBUG``
        Enable debug logging in the browser console (default ``False``).
    """

    def __init__(self, app: Optional[Flask] = None) -> None:
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Initialise the extension with a Flask application.

        This registers Jinja2 global functions so that templates can use
        ``{{ sanwo_scripts() }}``, ``{{ sanwo_checkout(...) }}``, and
        ``{{ sanwo_custom_amount(...) }}``.
        """
        app.config.setdefault("SANWO_PROVIDER", "paystack")
        app.config.setdefault("SANWO_PUBLIC_KEY", "")
        app.config.setdefault("SANWO_CURRENCY", "NGN")
        app.config.setdefault("SANWO_DEBUG", False)
        app.config.setdefault("SANWO_TEMPLATE_URL", None)
        app.config.setdefault("SANWO_TEMPLATE", None)

        # Create the client and store it on the app for later access.
        client = Sanwo(
            provider=app.config["SANWO_PROVIDER"],
            public_key=app.config["SANWO_PUBLIC_KEY"],
            currency=app.config["SANWO_CURRENCY"],
            debug=app.config["SANWO_DEBUG"],
            template_url=app.config["SANWO_TEMPLATE_URL"],
            template=app.config["SANWO_TEMPLATE"],
        )

        # Store on the app extensions dict so users can access it if needed.
        app.extensions["sanwo"] = client

        # Register Jinja2 globals.
        app.jinja_env.globals["sanwo_scripts"] = lambda: sanwo_scripts(client)
        app.jinja_env.globals["sanwo_checkout"] = lambda **kw: sanwo_checkout(
            client, **kw
        )
        app.jinja_env.globals["sanwo_custom_amount"] = (
            lambda **kw: sanwo_custom_amount(client, **kw)
        )
