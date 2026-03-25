from django.contrib import admin

from main import models


@admin.register(models.TShirtOrder)
class TShirtOrderAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "size", "quantity", "amount", "paid", "created_at"]
    list_filter = ["paid", "size", "color", "created_at"]
    search_fields = ["name", "email", "stripe_session_id"]
    date_hierarchy = "created_at"


@admin.register(models.Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ["title", "director_name", "email", "genre", "created_at"]
    list_filter = ["genre", "created_at"]
    search_fields = ["title", "director_name", "email"]
    date_hierarchy = "created_at"
