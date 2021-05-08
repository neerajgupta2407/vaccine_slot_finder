# Register your models here.
from django.contrib import admin

from app.models import TelegramAccount


class TelegramAccountAdmin(admin.ModelAdmin):
    list_display = [
        "username",
        "chat_id",
        "pincode",
        "registered_18",
        "registered_45",
        "alerts_18",
        "alerts_45",
    ]
    list_filter = ["pincode", "registered_18", "registered_45"]
    search_fields = ["pincode", "username"]
    date_hierarchy = "create_time"


admin.site.register(TelegramAccount, TelegramAccountAdmin)
