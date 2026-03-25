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


class TShirtOrder(models.Model):
    """T-shirt order from Stripe checkout."""

    SIZE_CHOICES = [
        ("XS", "Extra Small"),
        ("S", "Small"),
        ("M", "Medium"),
        ("L", "Large"),
        ("XL", "Extra Large"),
        ("XXL", "Double Extra Large"),
        ("XXXL", "Triple Extra Large"),
    ]

    COLOR_CHOICES = [
        ("darkgrey", "Dark Grey"),
        ("black", "Black"),
        ("white", "White"),
    ]

    name = models.CharField(max_length=200)
    email = models.EmailField()
    size = models.CharField(max_length=10, choices=SIZE_CHOICES, default="M")
    color = models.CharField(max_length=20, choices=COLOR_CHOICES, default="darkgrey")
    quantity = models.PositiveIntegerField(default=1)
    amount = models.PositiveIntegerField(help_text="Amount in GBP")
    paid = models.BooleanField(default=False)
    stripe_session_id = models.CharField(max_length=255, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"T-shirt order for {self.name} - £{self.amount}"
