from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint
from django.utils.translation import gettext_lazy as _


class Book(models.Model):
    class Cover(models.TextChoices):
        HARD = "HARD", _("Hard")
        SOFT = "SOFT", _("Soft")

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.CharField(max_length=4, choices=Cover.choices)
    inventory = models.IntegerField(validators=[MinValueValidator(0)])
    daily_fee = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["title", "author"]
        constraints = [
            UniqueConstraint(
                fields=["title", "author"], name="unique_title_and_author_combination"
            )
        ]

    def __str__(self):
        return f"{self.title} by {self.author}"
