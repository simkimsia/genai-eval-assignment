from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Q
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
        # Check for similar clients to help prevent duplicates
        return JsonResponse({"exists": False})


@login_required
@require_http_methods(["GET"])
def check_duplicate_client(request):
    """API endpoint to check for potential duplicate clients by name."""
    name = request.GET.get("name", "").strip()
    if not name:
        return JsonResponse({"duplicate_found": False})

    # Look for clients with similar names
    similar_clients = Client.objects.filter(
        Q(name__icontains=name) | Q(name__iexact=name)
    ).values("id", "name", "reference_number")[:5]

    return JsonResponse(
        {
            "duplicate_found": len(similar_clients) > 0,
            "similar_clients": list(similar_clients),
        }
    )


@login_required
@require_http_methods(["POST"])
def create_client(request):
    """API endpoint to create a new client."""
    try:
        data = request.json
        client = Client.objects.create(
            reference_number=data["reference_number"],
            name=data["name"],
            email=data.get("email", ""),
            phone=data.get("phone", ""),
            address=data.get("address", ""),
        )
        return JsonResponse({"success": True, "client_id": client.id})
    except ValidationError as e:
        return JsonResponse({"success": False, "error": str(e)})
    except Exception:
        return JsonResponse({"success": False, "error": "Error creating client"})


@login_required
@require_http_methods(["POST"])
def create_document_api(request):
    """API endpoint to create a new document and optionally a new client."""
    try:
        is_new_client = request.POST.get("is_new_client") == "true"
        reference_number = request.POST.get("reference_number")

        if not reference_number:
            return JsonResponse(
                {"success": False, "error": "Client reference number is required"},
                status=400,
            )

        # Handle client creation or retrieval
        if is_new_client:
            client_name = request.POST.get("client_name")
            if not client_name:
                return JsonResponse(
                    {
                        "success": False,
                        "error": "Client name is required for new clients",
                    },
                    status=400,
                )

            # Check if client with reference number already exists
            if Client.objects.filter(reference_number=reference_number).exists():
                return JsonResponse(
                    {
                        "success": False,
                        "error": "A client with this reference number already exists",
                    },
                    status=400,
                )

            # Create new client
            client = Client.objects.create(
                reference_number=reference_number,
                name=client_name,
                email=request.POST.get("client_email", ""),
                phone=request.POST.get("client_phone", ""),
                address=request.POST.get("client_address", ""),
            )
        else:
            # Get existing client
            client_id = request.POST.get("client_id")
            try:
                client = Client.objects.get(id=client_id)
            except Client.DoesNotExist:
                return JsonResponse(
                    {"success": False, "error": "Client not found"}, status=400
                )

        # Validate required document fields
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

        if "file" not in request.FILES:
            return JsonResponse(
                {"success": False, "error": "Document file is required"}, status=400
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
    except ValidationError as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)
    except Exception as e:
        return JsonResponse(
            {"success": False, "error": f"Error creating document: {str(e)}"},
            status=400,
        )


@login_required
def view_document(request, document_id):
    """View for displaying document details."""
    document = get_object_or_404(Document, id=document_id)
    return render(request, "documents/view.html", {"document": document})
