from rest_framework import generics, status
from .serializers import ProviderSerializer
from django.shortcuts import get_object_or_404
import csv, zipfile, io
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.template.loader import render_to_string
from weasyprint import HTML
from django.http import HttpResponse, JsonResponse
from .models import Provider
from billing.models import AuditLog


def log_audit(user, action, description):
    AuditLog.objects.create(
        user=str(user),
        action_type=action,
        description=description
    )

def export_provider_pdf(request):
    # Temporary simple implementation
    return HttpResponse("Export Provider PDF - Placeholder")
    
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def export_providers_pdf(request):
    providers = Provider.objects.all().order_by("provider_name")
    html = render_to_string("pdf/provider_list_pdf.html", {"providers": providers})
    pdf = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf()
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = 'inline; filename="providers_list.pdf"'
    return response

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def export_providers_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="providers_list.csv"'
    writer = csv.writer(response)
    writer.writerow(["Name", "NPI", "Compliance Status", "Certification"])
    for provider in Provider.objects.all().order_by("provider_name"):
        writer.writerow([
            provider.provider_name,
            provider.npi,
            provider.compliance_status,
            provider.certification
        ])
    return response

class ProviderListView(generics.ListAPIView):
    queryset = Provider.objects.all().order_by("provider_name")
    serializer_class = ProviderSerializer
    permission_classes = [IsAuthenticated]

class ProviderDetailView(generics.RetrieveAPIView):
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

class ProviderUpdateView(generics.UpdateAPIView):
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def perform_update(self, serializer):
        instance = serializer.save()
        log_audit(self.request.user, "update", f"Updated provider: {instance.provider_name}")

class ProviderCreateView(generics.CreateAPIView):
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        instance = serializer.save()
        log_audit(self.request.user, "create", f"Created provider: {instance.provider_name}")

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_provider(request, id):
    provider = get_object_or_404(Provider, id=id)
    provider_name = provider.provider_name
    provider.delete()
    log_audit(request.user, "delete", f"Deleted provider: {provider_name}")
    return JsonResponse({"message": "Provider deleted successfully."})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def export_providers_zip(request):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as zip_file:
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)
        writer.writerow(["Name", "NPI", "Compliance Status", "Certification"])
        for provider in Provider.objects.all().order_by("provider_name"):
            writer.writerow([
                provider.provider_name,
                provider.npi,
                provider.compliance_status,
                provider.certification
            ])
        zip_file.writestr("providers.csv", csv_buffer.getvalue())
        html = render_to_string("pdf/provider_list_pdf.html", {
            "providers": Provider.objects.all().order_by("provider_name")
        })
        pdf_bytes = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf()
        zip_file.writestr("providers.pdf", pdf_bytes)

    buffer.seek(0)
    response = HttpResponse(buffer.read(), content_type="application/zip")
    response["Content-Disposition"] = 'attachment; filename="providers_export.zip"'
    return response

