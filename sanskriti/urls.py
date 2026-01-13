from django.urls import path
from .views import (
    Health,
    AdminLoginView,
    EnquiryCreateView,
    AdminEnquiryListView,
    ExportEnquiriesExcelView,
    ExportEnquiriesPDFView,
)

urlpatterns = [
    path("health/", Health.as_view(), name="health"),

    # public
    path("enquiries/", EnquiryCreateView.as_view(), name="enquiry-create"),

    # admin auth + admin APIs
    path("auth/admin/login/", AdminLoginView.as_view(), name="admin-login"),
    path("admin/enquiries/", AdminEnquiryListView.as_view(), name="admin-enquiry-list"),
    path("admin/enquiries/export/excel/", ExportEnquiriesExcelView.as_view(), name="export-excel"),
    path("admin/enquiries/export/pdf/", ExportEnquiriesPDFView.as_view(), name="export-pdf"),
]
