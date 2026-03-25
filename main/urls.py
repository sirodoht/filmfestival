from django.urls import path

from main import views

app_name = "main"

urlpatterns = [
    path("", views.index, name="index"),
    path("about/", views.about, name="about"),
    path("submit/", views.submit, name="submit"),
    path("submit/success/", views.submit_success, name="submit-success"),
    path("tshirt/order/", views.TShirtPurchaseView.as_view(), name="tshirt-order"),
    path("tshirt/success/", views.tshirt_success, name="tshirt-success"),
    path("tshirt/cancel/", views.tshirt_cancel, name="tshirt-cancel"),
    path("webhook/stripe/", views.stripe_webhook, name="stripe-webhook"),
]
