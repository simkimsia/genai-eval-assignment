from django.urls import path

from . import views

app_name = "law_firm_docs"

urlpatterns = [
    path("documents/create/", views.create_document, name="create_document"),
    path("documents/<int:document_id>/", views.view_document, name="view_document"),
    path(
        "api/client-lookup/<str:reference_number>/",
        views.client_lookup,
        name="client_lookup",
    ),
    path("api/create-client/", views.create_client, name="create_client"),
    path("api/create-document/", views.create_document_api, name="create_document_api"),
]
