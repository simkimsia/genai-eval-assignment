from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models


class Client(models.Model):
    """Represents a client in the law firm system."""

    class Meta:
        verbose_name = "client"
        verbose_name_plural = "clients"
        ordering = ["-created_at"]

    reference_number = models.CharField(
        max_length=50,
        validators=[
            RegexValidator(
                regex=r"^[A-Z0-9-]+$",
                message="Reference number must contain only uppercase letters, numbers, and hyphens",
            )
        ],
        help_text="Unique client reference number within the collection",
        unique=True,
    )
    name = models.CharField(max_length=255, help_text="Client's full name")
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, help_text="Additional notes about the client")

    def __str__(self):
        return f"{self.reference_number} - {self.name}"


class Document(models.Model):
    """Represents a document in the law firm system."""

    class Meta:
        verbose_name = "document"
        verbose_name_plural = "documents"
        ordering = ["-created_at"]

    DOCUMENT_TYPES = [
        ("contract", "Contract"),
        ("agreement", "Agreement"),
        ("letter", "Letter"),
        ("report", "Report"),
        ("memo", "Memo"),
        ("other", "Other"),
    ]

    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="documents"
    )
    title = models.CharField(max_length=255, help_text="Document title")
    document_type = models.CharField(
        max_length=20, choices=DOCUMENT_TYPES, default="other"
    )
    file = models.FileField(
        upload_to="documents/%Y/%m/", help_text="The actual document file"
    )
    description = models.TextField(blank=True, help_text="Document description")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_documents",
    )
    is_confidential = models.BooleanField(
        default=False, help_text="Mark if document contains confidential information"
    )
    tags = models.CharField(
        max_length=255, blank=True, help_text="Comma-separated tags for easy searching"
    )

    def __str__(self):
        return f"{self.title} - {self.client.reference_number}"

    def get_tags_list(self):
        """Returns a list of tags."""
        return [tag.strip() for tag in self.tags.split(",") if tag.strip()]
