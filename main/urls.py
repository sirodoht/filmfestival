from django.urls import path

from main import views

app_name = "main"

urlpatterns = [
    path("", views.index, name="index"),
    path("about/", views.about, name="about"),
    path("submit/", views.submit, name="submit"),
    path("submit/success/", views.submit_success, name="submit-success"),
]
