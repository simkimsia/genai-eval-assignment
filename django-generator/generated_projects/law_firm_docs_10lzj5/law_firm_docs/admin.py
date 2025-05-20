from django.contrib import admin

from .models import Client, Document


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("reference_number", "name", "email", "phone")
    search_fields = ("reference_number", "name", "email")
    list_filter = ("created_at",)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "client", "document_type", "is_confidential", "created_at")
    list_filter = ("document_type", "is_confidential", "created_at")
    search_fields = ("title", "client__name", "client__reference_number")
    date_hierarchy = "created_at"
