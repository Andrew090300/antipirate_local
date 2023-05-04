from django.contrib import admin

from Antipirate_ver_2.reports.models import ReportedLinkModel


@admin.register(ReportedLinkModel)
class ReportedLinkModelAdmin(admin.ModelAdmin):
    list_display = (
        "link",
        "domain",
        "music"
    )
    readonly_fields = (
        "link",
        "domain",
        "music"
    )
