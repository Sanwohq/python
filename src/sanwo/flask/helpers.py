"""Jinja2 helper functions for rendering Sanwo checkout elements.

These are registered as Jinja2 globals by :class:`~sanwo.flask.SanwoFlask`
and can also be called directly if you prefer.
"""

from __future__ import annotations

from typing import Optional

from markupsafe import Markup

from sanwo.client import Sanwo


def sanwo_scripts(client: Sanwo) -> Markup:
    """Return a ``<script>`` tag that loads the Sanwo CDN embed script.

    Usage in a Jinja2 template::

        {{ sanwo_scripts() }}
    """
    return client.render_script()


def sanwo_checkout(
    client: Sanwo,
    *,
    amount: int,
    email: str,
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
    """Render a Sanwo checkout button with inline JavaScript.

    Usage in a Jinja2 template::

        {{ sanwo_checkout(amount=500000, email="user@example.com") }}

    Parameters
    ----------
    amount:
        Amount in minor units (kobo / cents).
    email:
        Customer email address.
    description:
        Human-readable payment description.
    reference:
        Unique transaction reference (auto-generated if omitted).
    currency:
        Override the default currency.
    button_text:
        Label displayed on the button.
    button_class:
        CSS class(es) for the ``<button>`` element.
    first_name:
        Customer first name.
    last_name:
        Customer last name.
    phone:
        Customer phone number.
    callback:
        Name of a global JavaScript function to call on completion.
    """
    return client.render_checkout(
        amount=amount,
        email=email,
        description=description,
        reference=reference,
        currency=currency,
        button_text=button_text,
        button_class=button_class,
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        callback=callback,
    )


def sanwo_custom_amount(
    client: Sanwo,
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
    """Render a Sanwo custom-amount checkout widget.

    Usage in a Jinja2 template::

        {{ sanwo_custom_amount(email="user@example.com") }}

    Parameters
    ----------
    email:
        Customer email.  If omitted the widget prompts the user.
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
        Name of a global JavaScript function to call on completion.
    """
    return client.render_custom_amount(
        email=email,
        currency=currency,
        button_text=button_text,
        placeholder=placeholder,
        min_amount=min_amount,
        max_amount=max_amount,
        description=description,
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        callback=callback,
    )
