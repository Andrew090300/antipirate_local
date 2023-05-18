from django.contrib import admin

from Antipirate_ver_2.reports.models import ReportedLinkModel, FakeLinkModel


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


@admin.register(FakeLinkModel)
class FakeLinkModelAdmin(admin.ModelAdmin):
    list_display = (
        "link",
        "domain",
        "music",
        "created_at"
    )
    readonly_fields = (
        "link",
        "domain",
        "music",
        "created_at"
    )