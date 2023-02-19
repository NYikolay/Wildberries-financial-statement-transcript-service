from django.contrib import admin

from support.models import ContactMessage

# Register your models here.


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'message_type', 'user_name', 'created_at')
    list_filter = ('user', 'message_type', 'created_at')

