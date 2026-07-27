"""Optional Django views for webhook and verification endpoints.

These views provide a starting point for handling payment callbacks.
Override the handler methods in your own views for production use.
"""

from __future__ import annotations

import json
from typing import Any, Dict

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt


@method_decorator(csrf_exempt, name="dispatch")
class SanwoWebhookView(View):
    """Base view for receiving payment provider webhooks.

    Subclass this view and override :meth:`handle_webhook` to process
    incoming webhook payloads::

        from sanwo.django.views import SanwoWebhookView

        class MyWebhookView(SanwoWebhookView):
            def handle_webhook(self, payload):
                status = payload.get("status")
                reference = payload.get("reference")
                # ... verify and fulfill order ...
                return {"ok": True}

    Wire the view into your URL configuration::

        path("webhooks/sanwo/", MyWebhookView.as_view()),
    """

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        try:
            payload: Dict[str, Any] = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        result = self.handle_webhook(payload)
        if isinstance(result, HttpResponse):
            return result
        return JsonResponse(result if result is not None else {"ok": True})

    def handle_webhook(self, payload: Dict[str, Any]) -> Any:
        """Process the webhook payload.

        Override this method in your subclass.  Return a dict to be
        serialised as JSON, or return an ``HttpResponse`` directly.
        """
        return {"ok": True}


class SanwoVerifyView(View):
    """Base view for verifying a transaction reference.

    Subclass and override :meth:`verify_transaction`::

        from sanwo.django.views import SanwoVerifyView

        class MyVerifyView(SanwoVerifyView):
            def verify_transaction(self, reference):
                # Call your provider's verification API
                # Return a dict with the verification result
                return {"verified": True, "reference": reference}

    Wire the view into your URL configuration::

        path("verify/sanwo/", MyVerifyView.as_view()),
    """

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        reference = request.GET.get("reference", "")
        if not reference:
            return JsonResponse({"error": "reference is required"}, status=400)

        result = self.verify_transaction(reference)
        if isinstance(result, HttpResponse):
            return result
        return JsonResponse(result if result is not None else {"error": "Not implemented"}, status=501)

    def verify_transaction(self, reference: str) -> Any:
        """Verify a transaction by its reference.

        Override this method in your subclass.  Return a dict to be
        serialised as JSON, or return an ``HttpResponse`` directly.
        """
        return {"error": "Not implemented"}
