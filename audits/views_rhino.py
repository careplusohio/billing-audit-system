# /backend/audits/views_rhino.py
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.contrib import messages
from django.db.models import Q, Sum
from django.db import connection
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils.datastructures import MultiValueDictKeyError
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

import csv
import zipfile
import io
from weasyprint import HTML

from .models import RhinoClaim
from .serializers import RhinoClaimSerializer


@login_required
def rhino_claims_dashboard(request):
    query = request.GET.get('q', '')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    payer = request.GET.get('payer')

    claims = RhinoClaim.objects.all()

    if query:
        claims = claims.filter(
            Q(patient_first_name__icontains=query) |
            Q(patient_last_name__icontains=query) |
            Q(rb_claim_id__icontains=query) |
            Q(claim_status__icontains=query) |
            Q(payer__icontains=query)
        )

    if start_date:
        claims = claims.filter(date_of_service__gte=start_date)
    if end_date:
        claims = claims.filter(date_of_service__lte=end_date)
    if payer:
        claims = claims.filter(payer__icontains=payer)

    total_claims = claims.count()
    total_billed = claims.aggregate(Sum('total_billed'))['total_billed__sum'] or 0
    total_paid = claims.aggregate(Sum('total_paid'))['total_paid__sum'] or 0

    context = {
        "claims": claims.order_by("-created_date")[:200],
        "query": query,
        "total_claims": total_claims,
        "total_billed": total_billed,
        "total_paid": total_paid,
        "start_date": start_date,
        "end_date": end_date,
        "payer": payer,
    }
    return render(request, "audits/rhino_claims_dashboard.html", context)


@staff_member_required
def export_rhino_claims_pdf(request):
    claims = RhinoClaim.objects.all().order_by("-id")[:200]
    html_string = render_to_string("audits/rhino_claims_pdf.html", {"claims": claims})
    pdf_file = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = "attachment; filename=rhino_claims.pdf"
    return response


@staff_member_required
def export_rhino_claims_csv(request):
    claims = RhinoClaim.objects.all().order_by("-id")[:200]
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=rhino_claims.csv"

    writer = csv.writer(response)
    headers = [field.name for field in RhinoClaim._meta.fields]
    writer.writerow(headers)

    for claim in claims:
        writer.writerow([getattr(claim, field) for field in headers])

    return response


@staff_member_required
def export_rhino_claims_zip(request):
    claims = RhinoClaim.objects.all().order_by("-id")[:200]
    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, "w") as zip_file:
        csv_io = io.StringIO()
        writer = csv.writer(csv_io)
        headers = [field.name for field in RhinoClaim._meta.fields]
        writer.writerow(headers)

        for claim in claims:
            writer.writerow([getattr(claim, field) for field in headers])

        zip_file.writestr("rhino_claims.csv", csv_io.getvalue())

    buffer.seek(0)
    response = HttpResponse(buffer, content_type="application/zip")
    response["Content-Disposition"] = "attachment; filename=rhino_claims.zip"
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def rhino_claim_detail(request, id):
    try:
        claim = RhinoClaim.objects.get(id=id)
    except RhinoClaim.DoesNotExist:
        return Response({"error": "Rhino claim not found"}, status=404)

    serializer = RhinoClaimSerializer(claim)
    return Response(serializer.data)


@csrf_exempt
def upload_rhino_csv(request):
    if request.method == "POST":
        csv_file = request.FILES.get("file")
        if not csv_file or not csv_file.name.endswith('.csv'):
            return JsonResponse({"error": "Invalid file uploaded."}, status=400)

        decoded_file = csv_file.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)

        count = 0
        for row in reader:
            try:
                RhinoClaim.objects.create(
                    patient_first_name=row.get('patient_first_name', ''),
                    patient_last_name=row.get('patient_last_name', ''),
                    patient_dob=row.get('patient_dob', None),
                    date_of_service=row.get('date_of_service', None),
                    total_billed=row.get('total_billed') or 0,
                    total_paid=row.get('total_paid') or 0,
                    patient_payer=row.get('patient_payer', ''),
                    claim_status=row.get('claim_status', '')
                )
                count += 1
            except Exception as e:
                return JsonResponse({"error": f"Error on row {count + 1}: {str(e)}"}, status=400)

        return JsonResponse({"message": f"Successfully uploaded {count} claims."})

    return JsonResponse({"error": "Invalid request method."}, status=405)


@method_decorator(csrf_exempt, name='dispatch')

class RhinoCSVUploadView(APIView):
    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get("file")
        if not file_obj:
            return Response({"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)

        decoded_file = file_obj.read().decode("utf-8").splitlines()
        reader = csv.DictReader(decoded_file)
        required_fields = {"trading_partner_name", "patient_id", "date_of_service"}
        missing_fields = required_fields - set(reader.fieldnames)

        if missing_fields:
            return Response({
                "error": "Missing required fields in CSV: " + ", ".join(missing_fields)
            }, status=status.HTTP_400_BAD_REQUEST)

        # Just simulate accepting file for now
        return Response({"message": "CSV uploaded and validated successfully."})
