from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods

from .models import Client, Document


@login_required
def create_document(request):
    """View for the document creation form."""
    return render(request, "documents/create.html")


@login_required
@require_http_methods(["GET"])
def client_lookup(request, reference_number):
    """API endpoint to lookup a client by reference number."""
    try:
        client = Client.objects.get(reference_number=reference_number)
        return JsonResponse(
            {
                "exists": True,
                "client": {
                    "id": client.id,
                    "name": client.name,
                    "email": client.email,
                    "phone": client.phone,
                    "address": client.address,
                },
            }
        )
    except Client.DoesNotExist:
        return JsonResponse({"exists": False})


@login_required
@require_http_methods(["POST"])
def create_client(request):
    """API endpoint to create a new client."""
    try:
        # Ensure request body is parsed as JSON
        import json

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

        reference_number = data.get("reference_number")
        if not reference_number:
            return JsonResponse(
                {"success": False, "error": "Reference number is required"}, status=400
            )

        # Check if a client with this reference number already exists
        if Client.objects.filter(reference_number=reference_number).exists():
            return JsonResponse(
                {
                    "success": False,
                    "error": "Client with this reference number already exists",
                },
                status=409,  # HTTP 409 Conflict
            )

        client = Client.objects.create(
            reference_number=reference_number,
            name=data["name"],  # Assume name is required
            email=data.get("email", ""),
            phone=data.get("phone", ""),
            address=data.get("address", ""),
        )
        return JsonResponse(
            {"success": True, "client_id": client.id, "client_name": client.name}
        )
    except ValidationError as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)
    except KeyError as e:  # Handle missing 'name' key
        return JsonResponse(
            {"success": False, "error": f"Missing required field: {str(e)}"}, status=400
        )
    except Exception:  # Catch other potential errors
        # Log the exception for debugging
        # import logging
        # logging.error(f"Error creating client: {e}")
        return JsonResponse(
            {"success": False, "error": "Error creating client"}, status=500
        )


@login_required
@require_http_methods(["POST"])
def create_document_api(request):
    """API endpoint to create a new document."""
    try:
        client_id = request.POST.get("client_id")
        if not client_id:
            return JsonResponse(
                {"success": False, "error": "Client ID is required"}, status=400
            )

        client = Client.objects.get(id=client_id)

        # Validate required fields
        title = request.POST.get("title")
        if not title:
            return JsonResponse(
                {"success": False, "error": "Document title is required"}, status=400
            )

        document_type = request.POST.get("document_type")
        if not document_type:
            return JsonResponse(
                {"success": False, "error": "Document type is required"}, status=400
            )

        document = Document.objects.create(
            client=client,
            title=title,
            document_type=document_type,
            file=request.FILES.get("file"),
            description=request.POST.get("description", ""),
            is_confidential=request.POST.get("is_confidential") == "on",
            tags=request.POST.get("tags", ""),
            created_by=request.user,
        )

        return JsonResponse(
            {
                "success": True,
                "redirect_url": f"/documents/{document.id}/",
            }
        )
    except Client.DoesNotExist:
        return JsonResponse({"success": False, "error": "Client not found"}, status=400)
    except Exception:
        return JsonResponse(
            {"success": False, "error": "Error creating document"}, status=400
        )


@login_required
def view_document(request, document_id):
    """View for displaying document details."""
    document = get_object_or_404(Document, id=document_id)
    return render(request, "documents/view.html", {"document": document})
