"""FastAPI integration for Sanwo payments."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from fastapi import FastAPI
    from starlette.templating import Jinja2Templates

from sanwo.client import Sanwo
from sanwo.flask.helpers import (
    sanwo_checkout,
    sanwo_custom_amount,
    sanwo_scripts,
)


class SanwoFastAPI:
    """FastAPI integration that provides Sanwo payment helpers for Jinja2 templates.

    Can be used with any ``Jinja2Templates`` instance::

        from fastapi import FastAPI
        from sanwo.fastapi import SanwoFastAPI

        app = FastAPI()
        sanwo = SanwoFastAPI(
            app,
            provider="paystack",
            public_key="pk_test_xxx",
        )

    Or deferred with :meth:`init_app`::

        sanwo = SanwoFastAPI(provider="paystack", public_key="pk_test_xxx")
        sanwo.init_app(app)

    Configuration parameters:

    ``provider``
        Payment provider id (default ``"paystack"``).
    ``public_key``
        Provider public/publishable key (**required**).
    ``currency``
        ISO 4217 currency code (default ``"NGN"``).
    ``debug``
        Enable debug logging in the browser console (default ``False``).
    ``template_url``
        URL for custom provider template (default ``None``).
    ``template``
        Inline HTML for custom provider template (default ``None``).
    """

    def __init__(
        self,
        app: Optional[FastAPI] = None,
        *,
        provider: str = "paystack",
        public_key: str = "",
        currency: str = "NGN",
        debug: bool = False,
        template_url: Optional[str] = None,
        template: Optional[str] = None,
    ) -> None:
        self._provider = provider
        self._public_key = public_key
        self._currency = currency
        self._debug = debug
        self._template_url = template_url
        self._template = template
        self.client: Optional[Sanwo] = None

        if app is not None:
            self.init_app(app)

    def init_app(self, app: FastAPI) -> None:
        """Initialise the integration with a FastAPI application."""
        self.client = Sanwo(
            provider=self._provider,
            public_key=self._public_key,
            currency=self._currency,
            debug=self._debug,
            template_url=self._template_url,
            template=self._template,
        )
        app.state.sanwo = self.client

    def init_templates(self, templates: Jinja2Templates) -> None:
        """Register Sanwo helpers as Jinja2 globals on a ``Jinja2Templates`` instance."""
        if self.client is None:
            raise RuntimeError("Call init_app() before init_templates()")

        client = self.client
        env = templates.env
        env.globals["sanwo_scripts"] = lambda: sanwo_scripts(client)
        env.globals["sanwo_checkout"] = lambda **kw: sanwo_checkout(client, **kw)
        env.globals["sanwo_custom_amount"] = lambda **kw: sanwo_custom_amount(client, **kw)
