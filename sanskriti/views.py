import io
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone

from openpyxl import Workbook
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

from .models import Enquiry
from .serializers import EnquiryCreateSerializer, EnquiryListSerializer, AdminLoginSerializer

from django.utils import timezone  # ✅ add this

def ist_str(dt):
    if not dt:
        return ""
    return timezone.localtime(dt).strftime("%Y-%m-%d %H:%M:%S")

class Health(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        return Response({"ok": True})

class AdminLoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        ser = AdminLoginSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        return Response(ser.validated_data)

class EnquiryCreateView(generics.CreateAPIView):
    queryset = Enquiry.objects.all()
    serializer_class = EnquiryCreateSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        enquiry = serializer.save()

        # Notify admin via email
        to_email = getattr(settings, "ADMIN_NOTIFY_EMAIL", None)
        if to_email and settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD:
            subject = "New enquiry received from Sanskriti"
            message = (
                "A new enquiry has been submitted:\n\n"
                f"Name: {enquiry.name}\n"
                f"Mobile: {enquiry.mobile}\n"
                f"Email: {enquiry.email}\n"
                f"Time: {enquiry.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
            )
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[to_email],
                    fail_silently=True,
                )
            except Exception:
                # keep API success even if email fails
                pass

class AdminEnquiryListView(generics.ListAPIView):
    queryset = Enquiry.objects.all()
    serializer_class = EnquiryListSerializer
    permission_classes = [IsAdminUser]

class ExportEnquiriesExcelView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        wb = Workbook()
        ws = wb.active
        ws.title = "Enquiries"

        ws.append(["ID", "Name", "Mobile", "Email", "Created At"])
        for e in Enquiry.objects.all().order_by("-created_at"):
            ws.append([e.id, e.name, e.mobile, e.email, ist_str(e.created_at)])


        buff = io.BytesIO()
        wb.save(buff)
        buff.seek(0)

        resp = HttpResponse(
            buff.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        resp["Content-Disposition"] = 'attachment; filename="enquiries.xlsx"'
        return resp

class ExportEnquiriesPDFView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        buff = io.BytesIO()
        doc = SimpleDocTemplate(buff, pagesize=A4, title="Enquiries")
        styles = getSampleStyleSheet()

        elements = [
            Paragraph("Enquiries Report", styles["Title"]),
            Spacer(1, 12),
        ]

        data = [["ID", "Name", "Mobile", "Email", "Created At"]]
        for e in Enquiry.objects.all().order_by("-created_at"):
            data.append([str(e.id), e.name, e.mobile, e.email, ist_str(e.created_at)])


        tbl = Table(data, repeatRows=1, colWidths=[40, 120, 90, 150, 110])
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.black),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
        ]))
        elements.append(tbl)
        doc.build(elements)

        pdf = buff.getvalue()
        buff.close()

        resp = HttpResponse(pdf, content_type="application/pdf")
        resp["Content-Disposition"] = 'attachment; filename="enquiries.pdf"'
        return resp
