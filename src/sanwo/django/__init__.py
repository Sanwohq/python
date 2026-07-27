"""Sanwo Django integration.

Add ``'sanwo.django'`` to ``INSTALLED_APPS`` and configure the following
settings::

    SANWO_PROVIDER = 'paystack'
    SANWO_PUBLIC_KEY = 'pk_test_xxx'
    SANWO_CURRENCY = 'NGN'      # optional, defaults to NGN
    SANWO_DEBUG = False          # optional

Then in your templates::

    {% load sanwo_tags %}
    {% sanwo_scripts %}
    {% sanwo_checkout amount=500000 email="user@example.com" %}
"""

default_app_config = "sanwo.django.apps.SanwoDjangoConfig"
