from django.contrib import admin
from Antipirate_ver_2.whitelist.models import WhiteListDomain


@admin.register(WhiteListDomain)
class WhiteListDomainAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "domain",

    )
