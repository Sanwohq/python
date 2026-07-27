"""Django AppConfig for Sanwo."""

from __future__ import annotations

from django.apps import AppConfig


class SanwoDjangoConfig(AppConfig):
    """Django application configuration for sanwo.django."""

    name = "sanwo.django"
    label = "sanwo"
    verbose_name = "Sanwo Payments"
    default_auto_field = "django.db.models.BigAutoField"
