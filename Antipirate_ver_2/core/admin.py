from django.contrib import admin
from django.contrib.auth.models import Group

from Antipirate_ver_2.core.models import Core

admin.site.unregister(Group)


@admin.register(Core)
class CoreAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "is_running",
        "in_process",
    )
    readonly_fields = (
        "title",
        "is_running",
      #  "in_process",
    )
    change_list_template = "core/core_admin.html"

    def changelist_view(self, request, extra_context=None):
        core = Core.objects.first()
        if request.method == 'POST':
            core.is_running = True if request.POST.get('ON') else False
            core.save(update_fields=('is_running',))
        response = super().changelist_view(
            request, extra_context, )
        return response

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
