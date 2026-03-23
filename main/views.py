from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import redirect, render

from main import forms


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
- Duration: {submission.duration} seconds
- Genre: {submission.get_genre_display()}
- Year: {submission.year_produced}
- Film Link: {submission.film_link}

We look forward to reviewing your film. The festival screening will take place on 8 August 2026 at Heartfort, London.

Looking forward to seeing you there!

Best regards,
The Heartfort Flash Film Festival Team
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
