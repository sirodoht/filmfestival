import contextlib
import logging

import stripe
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from main import forms, models

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY

TSHIRT_PRICE = 20  # £20 per t-shirt


def index(request):
    return render(request, "main/index.html")


def about(request):
    return render(request, "main/about.html")


def submit(request):
    if request.method == "POST":
        form = forms.SubmissionForm(request.POST)
        if form.is_valid():
            submission = form.save()

            # Send confirmation email
            subject = "Film Submission Received - Heartfort Flash Film Festival"
            message = f"""Dear {submission.director_name},

Thank you for submitting "{submission.title}" to the Heartfort Flash Film Festival.

Submission Details:
- Title: {submission.title}
- Director: {submission.director_name}
- Genre: {submission.genre}
- Film Link: {submission.film_link}

We look forward to reviewing your film. The festival screening will take place
on 8 August 2026 at Heartfort, London.

Looking forward to seeing you there!

Best regards,
HFFF Team
"""
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [submission.email]

            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=recipient_list,
                fail_silently=False,
            )

            return redirect("main:submit-success")
    else:
        form = forms.SubmissionForm()

    return render(request, "main/submit.html", {"form": form})


def submit_success(request):
    return render(request, "main/submit_success.html")


def tshirt_success(request):
    """Display success page with order details if session_id is provided."""
    session_id = request.GET.get("session_id")
    order = None
    if session_id:
        with contextlib.suppress(models.TShirtOrder.DoesNotExist):
            order = models.TShirtOrder.objects.get(stripe_session_id=session_id)
    return render(request, "main/tshirt_success.html", {"order": order})


def tshirt_cancel(request):
    return render(request, "main/tshirt_cancel.html")


class TShirtPurchaseView(View):
    """Handle t-shirt purchase and redirect to Stripe Checkout."""

    def post(self, request):
        """Create Stripe checkout session and redirect."""
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "gbp",
                            "product_data": {
                                "name": "Heartfort Flash Film Festival T-Shirt",
                                "description": "Official festival t-shirt",
                            },
                            "unit_amount": int(TSHIRT_PRICE * 100),
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url=request.build_absolute_uri("/tshirt/success/")
                + "?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=request.build_absolute_uri("/tshirt/cancel/"),
                custom_fields=[
                    {
                        "key": "size",
                        "label": {"type": "custom", "custom": "Size"},
                        "type": "dropdown",
                        "dropdown": {
                            "options": [
                                {"label": "XS", "value": "XS"},
                                {"label": "S", "value": "S"},
                                {"label": "M", "value": "M"},
                                {"label": "L", "value": "L"},
                                {"label": "XL", "value": "XL"},
                                {"label": "XXL", "value": "XXL"},
                                {"label": "XXXL", "value": "XXXL"},
                            ]
                        },
                    },
                    {
                        "key": "color",
                        "label": {"type": "custom", "custom": "Color"},
                        "type": "dropdown",
                        "dropdown": {
                            "options": [
                                {"label": "Dark Grey", "value": "darkgrey"},
                                {"label": "Black", "value": "black"},
                                {"label": "White", "value": "white"},
                            ]
                        },
                    },
                ],
                metadata={
                    "product": "tshirt",
                    "price": TSHIRT_PRICE,
                },
            )
            return redirect(session.url)
        except Exception:
            logger.exception("Failed to create Stripe checkout session for t-shirt")
            messages.error(
                request,
                "Something went wrong while initiating payment. Please try again.",
            )
            return redirect("main:index")


@csrf_exempt
@require_http_methods(["POST"])
def stripe_webhook(request):
    """Handle Stripe webhook events."""
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    if not settings.STRIPE_WEBHOOK_SECRET:
        logger.error("STRIPE_WEBHOOK_SECRET is not configured")
        return JsonResponse(
            {"status": "error", "message": "Webhook secret not configured"},
            status=500,
        )

    if not sig_header:
        logger.warning("Missing Stripe signature header")
        return JsonResponse(
            {"status": "error", "message": "Missing signature header"},
            status=400,
        )

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        logger.info(
            "Received Stripe webhook event: %s (id: %s)", event["type"], event["id"]
        )
    except ValueError as e:
        logger.error("Invalid payload: %s", e)
        return JsonResponse(
            {"status": "error", "message": "Invalid payload"},
            status=400,
        )
    except stripe.error.SignatureVerificationError as e:
        logger.error("Signature verification failed: %s", e)
        return JsonResponse(
            {"status": "error", "message": "Invalid signature"},
            status=400,
        )
    except Exception as e:
        logger.error("Unexpected error during webhook construction: %s", e)
        return JsonResponse(
            {"status": "error", "message": "Webhook processing error"},
            status=500,
        )

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        session_id = session.get("id", "unknown")

        try:
            metadata = session.get("metadata", {})
            product = metadata.get("product")
            customer_details = session.get("customer_details", {})
            customer_email = customer_details.get("email")

            if not product:
                logger.error(
                    "Missing product in session metadata (session: %s)", session_id
                )
                return JsonResponse(
                    {"status": "error", "message": "Missing product in metadata"},
                    status=200,
                )

            if not customer_email:
                logger.error(
                    "Missing customer email in session (session: %s)", session_id
                )
                return JsonResponse(
                    {"status": "error", "message": "Missing customer email"},
                    status=200,
                )

            if product == "tshirt":
                customer_details = session.get("customer_details", {})
                amount_total = session.get("amount_total")

                if amount_total is None:
                    logger.error(
                        "Missing amount_total in session (session: %s)", session_id
                    )
                    return JsonResponse(
                        {"status": "error", "message": "Missing amount_total"},
                        status=200,
                    )

                # Get size and color from custom fields
                size = "M"
                color = "darkgrey"
                custom_fields = session.get("custom_fields", [])
                for field in custom_fields:
                    if field.get("key") == "size":
                        dropdown = field.get("dropdown", {})
                        size = dropdown.get("value", "M")
                    elif field.get("key") == "color":
                        dropdown = field.get("dropdown", {})
                        color = dropdown.get("value", "darkgrey")

                # Create order record
                order = models.TShirtOrder.objects.create(
                    name=customer_details.get("name") or "",
                    email=customer_email,
                    size=size,
                    color=color,
                    quantity=1,
                    amount=TSHIRT_PRICE,
                    paid=True,
                    stripe_session_id=session_id,
                )
                logger.info(
                    "Created t-shirt order %s with size %s and color %s",
                    order.id,
                    size,
                    color,
                )

                # Send confirmation email
                try:
                    subject = "T-Shirt Order Confirmed - Heartfort Flash Film Festival"
                    message = f"""Dear {order.name},

Thank you for your t-shirt pre-order!

Order Details:
- Order ID: {order.id}
- Festival T-Shirt (Size: {order.get_size_display()}, Color: {order.get_color_display()})
- Quantity: {order.quantity}
- Total: £{order.amount}

This is a pre-order for pickup at the festival on 8 August 2026 at Heartfort, London.

Best regards,
HFFF Team
"""
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[order.email],
                        fail_silently=False,
                    )
                    logger.info("Sent confirmation email for order %s", order.id)
                except Exception:
                    logger.exception(
                        "Failed to send confirmation email for order %s", order.id
                    )

                return JsonResponse(
                    {"status": "success", "message": "Order processed successfully"},
                    status=200,
                )

        except Exception as e:
            logger.exception(
                "Unexpected error processing checkout.session.completed (session: %s): %s",
                session_id,
                e,
            )
            return JsonResponse(
                {"status": "error", "message": "Processing error"},
                status=500,
            )

    return JsonResponse({"status": "success", "message": "Event received"})
