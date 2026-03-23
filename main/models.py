from django.db import models


class Submission(models.Model):
    GENRE_CHOICES = [
        ("narrative", "Narrative"),
        ("documentary", "Documentary"),
        ("experimental", "Experimental"),
        ("animation", "Animation"),
    ]

    title = models.CharField(max_length=200)
    director_name = models.CharField(max_length=200)
    email = models.EmailField()
    duration = models.PositiveIntegerField(help_text="Duration in seconds (max 90)")
    synopsis = models.TextField()
    genre = models.CharField(max_length=50)
    film_link = models.URLField(help_text="Link to your film (Vimeo, YouTube, etc.)")
    consent = models.BooleanField(
        default=False,
        help_text="I give permission to use the above info for promotional material",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} by {self.director_name}"
