from django.contrib import admin
from django.shortcuts import render
from django.urls import path
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import ReporteDummy

class ReportesAdminView(admin.ModelAdmin):
    change_list_template = "admin/reportes_dashboard.html"
    verbose_name = "Reportes"
    verbose_name_plural = "Reportes"

    def changelist_view(self, request, extra_context=None):
        return render(request, "admin/reportes_dashboard.html")


class ReportesAdmin(admin.ModelAdmin):
    change_list_template = "admin/reportes_dashboard.html"

    def changelist_view(self, request, extra_context=None):
        return render(request, "admin/reportes_dashboard.html")

admin.site.register(ReporteDummy, ReportesAdmin)


