# Register your models here.
from django.contrib import admin

from app.models import *


class TelegramAccountAdmin(admin.ModelAdmin):
    list_display = [
        "username",
        "chat_id",
        "recent_searches",
        "saved_alerts",
        "alerts_18",
        "alerts_45",
        "is_active",
        "create_time",
    ]
    list_filter = ["pincode", "registered_18", "registered_45", "is_active"]
    search_fields = ["pincode", "username"]
    date_hierarchy = "create_time"


class DisrtictAdmin(admin.ModelAdmin):
    list_display = ["__str__"]
    list_filter = ["state"]


admin.site.register(TelegramAccount, TelegramAccountAdmin)
admin.site.register(States)
admin.site.register(Disrtict, DisrtictAdmin)
