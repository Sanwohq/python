"""Main Sanwo client for generating checkout HTML and JavaScript."""

from __future__ import annotations

import json
import uuid
from typing import Any, Dict, Optional, Union

from markupsafe import Markup, escape

from sanwo.exceptions import SanwoCheckoutError, SanwoConfigurationError
from sanwo.providers import resolve_provider
from sanwo.types import ProviderConfig, SanwoConfig

_CDN_URL = "https://cdn.jsdelivr.net/npm/@sanwohq/embed/dist/sanwo.global.js"


class Sanwo:
    """Sanwo payment client.

    Generates HTML and JavaScript for embedding Sanwo checkout buttons into
    server-rendered pages.  This class does **not** make any HTTP requests; it
    produces front-end markup that delegates to the Sanwo embed script loaded
    from the CDN.

    Parameters
    ----------
    provider:
        A :class:`~sanwo.types.ProviderConfig` instance (e.g.
        ``providers.PAYSTACK``) or a string ID such as ``"paystack"``.
    public_key:
        Your provider's public / publishable key.
    currency:
        ISO 4217 currency code used when no currency is specified at checkout
        time.  Defaults to ``"NGN"``.
    debug:
        When ``True`` the embed script logs checkout events to the browser
        console.
    """

    def __init__(
        self,
        provider: Union[str, ProviderConfig],
        public_key: str,
        currency: str = "NGN",
        debug: bool = False,
        template_url: Optional[str] = None,
        template: Optional[str] = None,
    ) -> None:
        if not public_key:
            raise SanwoConfigurationError("public_key is required")

        self._provider = resolve_provider(provider)

        if self._provider.id == "custom" and not template and not template_url:
            raise SanwoConfigurationError(
                'Custom provider requires a "template" or "template_url"'
            )

        self._config = SanwoConfig(
            provider=self._provider.id,
            public_key=public_key,
            currency=currency,
            debug=debug,
            template_url=template_url,
            template=template,
        )

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    @property
    def provider(self) -> ProviderConfig:
        """The resolved provider configuration."""
        return self._provider

    @property
    def public_key(self) -> str:
        return self._config.public_key

    @property
    def currency(self) -> str:
        return self._config.currency

    @property
    def debug(self) -> bool:
        return self._config.debug

    @property
    def script_url(self) -> str:
        return self._config.script_url

    @property
    def template_url(self) -> Optional[str]:
        return self._config.template_url

    @property
    def template(self) -> Optional[str]:
        return self._config.template

    def get_config(self) -> Dict[str, Any]:
        """Return the current configuration as a plain dictionary.

        Useful for passing config values into your own templates.
        """
        cfg: Dict[str, Any] = {
            "provider": self._config.provider,
            "public_key": self._config.public_key,
            "currency": self._config.currency,
            "debug": self._config.debug,
            "script_url": self._config.script_url,
        }
        if self._config.template_url:
            cfg["template_url"] = self._config.template_url
        if self._config.template:
            cfg["template"] = self._config.template
        return cfg

    # ------------------------------------------------------------------
    # HTML / JS rendering
    # ------------------------------------------------------------------

    def render_script(self) -> Markup:
        """Return a ``<script>`` tag that loads the Sanwo embed script."""
        return Markup(
            '<script src="{src}"></script>'.format(src=escape(self._config.script_url))
        )

    def render_checkout(
        self,
        amount: int,
        email: str,
        *,
        description: Optional[str] = None,
        reference: Optional[str] = None,
        currency: Optional[str] = None,
        button_text: str = "Pay Now",
        button_class: str = "sanwo-button",
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        phone: Optional[str] = None,
        callback: Optional[str] = None,
    ) -> Markup:
        """Render a complete checkout button with inline JavaScript.

        The returned HTML contains:

        * A ``<button>`` element styled with *button_class*.
        * An inline ``<script>`` that uses ``window.Sanwo.create()`` and
          ``.checkout()`` to initiate the payment when the button is clicked.

        All amounts are in **minor units** (kobo / cents).

        Parameters
        ----------
        amount:
            Amount in minor units (e.g. ``500000`` for NGN 5,000.00).
        email:
            Customer email address.
        description:
            Human-readable description of the payment.
        reference:
            Unique transaction reference.  Auto-generated if omitted.
        currency:
            Override the default currency for this checkout.
        button_text:
            Label displayed on the button.
        button_class:
            CSS class(es) applied to the button.
        first_name:
            Customer first name.
        last_name:
            Customer last name.
        phone:
            Customer phone number.
        callback:
            Name of a global JavaScript function to call on completion.
        """
        self._validate_checkout(amount, email)

        ref = reference or f"sanwo_{uuid.uuid4().hex[:16]}"
        cur = currency or self._config.currency
        btn_id = f"sanwo-btn-{uuid.uuid4().hex[:8]}"

        # Build the customer object for the JS payload.
        customer_parts: Dict[str, str] = {"email": email}
        if first_name:
            customer_parts["firstName"] = first_name
        if last_name:
            customer_parts["lastName"] = last_name
        if phone:
            customer_parts["phone"] = phone

        # Build the checkout options dict that will be JSON-serialised.
        checkout_opts: Dict[str, Any] = {
            "amount": amount,
            "currency": cur,
            "reference": ref,
            "customer": customer_parts,
        }
        if description:
            checkout_opts["description"] = description

        config_json = json.dumps(self._build_create_config())
        opts_json = json.dumps(checkout_opts)
        debug_flag = "true" if self._config.debug else "false"
        callback_js = ""
        if callback:
            cb = escape(callback)
            callback_js = (
                f"if (typeof window['{cb}'] === 'function') "
                f"{{ window['{cb}'](result); }}"
            )

        html = (
            f'<button type="button" class="{escape(button_class)}" '
            f'id="{btn_id}">{escape(button_text)}</button>\n'
            f"<script>\n"
            f"(function() {{\n"
            f"  var btn = document.getElementById('{btn_id}');\n"
            f"  btn.addEventListener('click', function() {{\n"
            f"    if (btn.disabled) return;\n"
            f"    btn.disabled = true;\n"
            f"    var sanwo = Sanwo.create({config_json});\n"
            f"    if ({debug_flag}) console.log('[Sanwo] Starting checkout', {opts_json});\n"
            f"    sanwo.checkout({opts_json}).then(function(result) {{\n"
            f"      btn.disabled = false;\n"
            f"      if ({debug_flag}) console.log('[Sanwo] Result', result);\n"
            f"      {callback_js}\n"
            f"    }}).catch(function(err) {{\n"
            f"      btn.disabled = false;\n"
            f"      console.error('[Sanwo] Checkout error:', err);\n"
            f"    }});\n"
            f"  }});\n"
            f"}})();\n"
            f"</script>"
        )
        return Markup(html)

    def render_custom_amount(
        self,
        *,
        email: Optional[str] = None,
        currency: Optional[str] = None,
        button_text: str = "Pay Now",
        placeholder: str = "Enter amount",
        min_amount: Optional[int] = None,
        max_amount: Optional[int] = None,
        description: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        phone: Optional[str] = None,
        callback: Optional[str] = None,
    ) -> Markup:
        """Render a custom-amount checkout widget.

        This produces an ``<input>`` for the amount (displayed in major
        units) and a pay button.  When submitted, the value is converted to
        minor units automatically.

        Parameters
        ----------
        email:
            Customer email.  If omitted the widget will prompt the user.
        currency:
            Override the default currency.
        button_text:
            Label for the pay button.
        placeholder:
            Placeholder text for the amount input.
        min_amount:
            Minimum amount in minor units.
        max_amount:
            Maximum amount in minor units.
        description:
            Human-readable payment description.
        first_name:
            Customer first name.
        last_name:
            Customer last name.
        phone:
            Customer phone number.
        callback:
            Name of a global JS function to call on completion.
        """
        cur = currency or self._config.currency
        widget_id = f"sanwo-custom-{uuid.uuid4().hex[:8]}"

        config_json = json.dumps(self._build_create_config())
        debug_flag = "true" if self._config.debug else "false"

        # Build data attributes for the div (matching Laravel pattern).
        attrs = [
            f'data-sanwo-provider="{escape(self._config.provider)}"',
            f'data-sanwo-key="{escape(self._config.public_key)}"',
            f'data-sanwo-currency="{escape(cur)}"',
            'data-sanwo-custom-amount="true"',
            f'data-sanwo-button-text="{escape(button_text)}"',
            f'data-sanwo-placeholder="{escape(placeholder)}"',
        ]
        if self._config.debug:
            attrs.append('data-sanwo-debug="true"')
        if self._config.template_url:
            attrs.append(f'data-sanwo-template-url="{escape(self._config.template_url)}"')
        if self._config.template:
            attrs.append(f'data-sanwo-template="{escape(self._config.template)}"')
        if email:
            attrs.append(f'data-sanwo-email="{escape(email)}"')
        if min_amount is not None:
            attrs.append(f'data-sanwo-min-amount="{min_amount}"')
        if max_amount is not None:
            attrs.append(f'data-sanwo-max-amount="{max_amount}"')
        if description:
            attrs.append(f'data-sanwo-description="{escape(description)}"')
        if first_name:
            attrs.append(f'data-sanwo-first-name="{escape(first_name)}"')
        if last_name:
            attrs.append(f'data-sanwo-last-name="{escape(last_name)}"')
        if phone:
            attrs.append(f'data-sanwo-phone="{escape(phone)}"')
        if callback:
            attrs.append(f'data-sanwo-callback="{escape(callback)}"')

        attrs_str = " ".join(attrs)

        # Build customer fields for JS.
        customer_fields: list[str] = []
        if email:
            customer_fields.append(f"email: {json.dumps(email)}")
        if first_name:
            customer_fields.append(f"firstName: {json.dumps(first_name)}")
        if last_name:
            customer_fields.append(f"lastName: {json.dumps(last_name)}")
        if phone:
            customer_fields.append(f"phone: {json.dumps(phone)}")
        customer_js = "{ " + ", ".join(customer_fields) + " }" if customer_fields else "{ email: emailInput.value }"

        callback_js = ""
        if callback:
            cb = escape(callback)
            callback_js = (
                f"if (typeof window['{cb}'] === 'function') "
                f"{{ window['{cb}'](result); }}"
            )

        min_check = ""
        if min_amount is not None:
            min_major = min_amount / 100
            min_check = (
                f"if (amountMinor < {min_amount}) {{ "
                f"alert('Minimum amount is {min_major:.2f}'); return; }}\n      "
            )
        max_check = ""
        if max_amount is not None:
            max_major = max_amount / 100
            max_check = (
                f"if (amountMinor > {max_amount}) {{ "
                f"alert('Maximum amount is {max_major:.2f}'); return; }}\n      "
            )

        email_input_html = ""
        email_input_js = ""
        if not email:
            email_input_html = (
                f'\n  <input type="email" id="{widget_id}-email" '
                f'placeholder="Email address" required '
                f'style="display:block;margin-bottom:8px;padding:8px;width:100%;box-sizing:border-box;" />'
            )
            email_input_js = f"var emailInput = document.getElementById('{widget_id}-email');\n      "

        html = (
            f'<div id="{widget_id}" {attrs_str}>'
            f"{email_input_html}\n"
            f'  <input type="number" id="{widget_id}-amount" '
            f'placeholder="{escape(placeholder)}" step="0.01" min="0" required '
            f'style="display:block;margin-bottom:8px;padding:8px;width:100%;box-sizing:border-box;" />\n'
            f'  <button type="button" id="{widget_id}-btn" class="sanwo-button">'
            f"{escape(button_text)}</button>\n"
            f"</div>\n"
            f"<script>\n"
            f"(function() {{\n"
            f"  var btn = document.getElementById('{widget_id}-btn');\n"
            f"  var amountInput = document.getElementById('{widget_id}-amount');\n"
            f"  {email_input_js}"
            f"  btn.addEventListener('click', function() {{\n"
            f"    var amountMajor = parseFloat(amountInput.value);\n"
            f"    if (isNaN(amountMajor) || amountMajor <= 0) {{ alert('Please enter a valid amount.'); return; }}\n"
            f"    var amountMinor = Math.round(amountMajor * 100);\n"
            f"    {min_check}{max_check}"
            f"    btn.disabled = true;\n"
            f"    var sanwo = Sanwo.create({config_json});\n"
            f"    var opts = {{\n"
            f"      amount: amountMinor,\n"
            f"      currency: {json.dumps(cur)},\n"
            f"      customer: {customer_js}\n"
            f"    }};\n"
        )
        if description:
            html += f"    opts.description = {json.dumps(description)};\n"
        html += (
            f"    if ({debug_flag}) console.log('[Sanwo] Starting checkout', opts);\n"
            f"    sanwo.checkout(opts).then(function(result) {{\n"
            f"      btn.disabled = false;\n"
            f"      if ({debug_flag}) console.log('[Sanwo] Result', result);\n"
            f"      {callback_js}\n"
            f"    }}).catch(function(err) {{\n"
            f"      btn.disabled = false;\n"
            f"      console.error('[Sanwo] Checkout error:', err);\n"
            f"    }});\n"
            f"  }});\n"
            f"}})();\n"
            f"</script>"
        )
        return Markup(html)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _build_create_config(self) -> Dict[str, Any]:
        cfg: Dict[str, Any] = {
            "provider": self._config.provider,
            "publicKey": self._config.public_key,
        }
        if self._config.template_url:
            cfg["templateUrl"] = self._config.template_url
        if self._config.template:
            cfg["template"] = self._config.template
        return cfg

    @staticmethod
    def _validate_checkout(amount: int, email: str) -> None:
        if not isinstance(amount, int) or amount <= 0:
            raise SanwoCheckoutError(
                "amount must be a positive integer (in minor units)"
            )
        if not email or "@" not in email:
            raise SanwoCheckoutError("A valid email address is required")
