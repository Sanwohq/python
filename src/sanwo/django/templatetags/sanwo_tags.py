"""Django template tags for Sanwo checkout integration.

Usage::

    {% load sanwo_tags %}

    {# Load the Sanwo embed script (place in <head> or before </body>) #}
    {% sanwo_scripts %}

    {# Render a checkout button with a fixed amount #}
    {% sanwo_checkout amount=500000 email="user@example.com" %}

    {# Render a custom-amount widget #}
    {% sanwo_custom_amount email="user@example.com" %}
"""

from __future__ import annotations

from django import template
from markupsafe import Markup

from sanwo.django.conf import get_sanwo_client

register = template.Library()


@register.simple_tag
def sanwo_scripts() -> str:
    """Output a ``<script>`` tag that loads the Sanwo embed CDN script."""
    client = get_sanwo_client()
    return client.render_script()


@register.simple_tag
def sanwo_checkout(
    amount: int,
    email: str,
    description: str = "",
    reference: str = "",
    currency: str = "",
    button_text: str = "Pay Now",
    button_class: str = "sanwo-button",
    first_name: str = "",
    last_name: str = "",
    phone: str = "",
    callback: str = "",
) -> str:
    """Render a Sanwo checkout button.

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
    client = get_sanwo_client()
    return client.render_checkout(
        amount=int(amount),
        email=email,
        description=description or None,
        reference=reference or None,
        currency=currency or None,
        button_text=button_text,
        button_class=button_class,
        first_name=first_name or None,
        last_name=last_name or None,
        phone=phone or None,
        callback=callback or None,
    )


@register.simple_tag
def sanwo_custom_amount(
    email: str = "",
    currency: str = "",
    button_text: str = "Pay Now",
    placeholder: str = "Enter amount",
    min_amount: int = 0,
    max_amount: int = 0,
    description: str = "",
    first_name: str = "",
    last_name: str = "",
    phone: str = "",
    callback: str = "",
) -> str:
    """Render a Sanwo custom-amount checkout widget.

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
        Minimum amount in minor units (0 = no minimum).
    max_amount:
        Maximum amount in minor units (0 = no maximum).
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
    client = get_sanwo_client()
    return client.render_custom_amount(
        email=email or None,
        currency=currency or None,
        button_text=button_text,
        placeholder=placeholder,
        min_amount=int(min_amount) if min_amount else None,
        max_amount=int(max_amount) if max_amount else None,
        description=description or None,
        first_name=first_name or None,
        last_name=last_name or None,
        phone=phone or None,
        callback=callback or None,
    )
