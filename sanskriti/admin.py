from django.contrib import admin
from .models import Enquiry

@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "mobile", "email", "created_at")
    list_filter = ("created_at",)
    search_fields = ("name", "mobile", "email")
