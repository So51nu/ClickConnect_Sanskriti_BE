from django.db import models
from django.core.validators import RegexValidator

class Enquiry(models.Model):
    name = models.CharField(max_length=120)
    mobile = models.CharField(
        max_length=15,
        validators=[RegexValidator(regex=r"^\+?\d{10,15}$", message="Enter a valid phone number.")],
    )
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.mobile})"
