from datetime import datetime

from django.contrib import admin

from users.models import (User, WBApiKey, SaleObject,
                          ClientUniqueProduct, NetCost, SaleReport, TaxRate,
                          IncorrectReport, UnloadedReports, UserSubscription, UserDiscount, Order)


admin.site.register(NetCost)
admin.site.register(TaxRate)
admin.site.register(IncorrectReport)
admin.site.register(UnloadedReports)
admin.site.register(UserDiscount)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_filter = ('is_active', 'date_joined')
    search_fields = ['email']
    list_display = ('email', 'date_joined', 'phone')


@admin.register(SaleObject)
class SaleObjectAdmin(admin.ModelAdmin):
    list_display = ('id', '__str__')
    search_fields = ('nm_id', 'id')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_filter = ('status', 'created_at')
    list_display = ('user', 'status', 'paid_sum', 'created_at')


@admin.register(WBApiKey)
class WBApiKeyAdmin(admin.ModelAdmin):
    search_fields = ('user', )
    list_filter = (
        'last_reports_update',
        'is_wb_data_loaded',
        'is_products_loaded',
        'last_reports_update',
        'is_active_import'
    )
    list_display = (
        '__str__',
        'is_wb_data_loaded',
        'is_products_loaded',
        'is_active_import',
        'last_reports_update',
        'created_at'
    )


@admin.register(ClientUniqueProduct)
class ClientUniqueProductAdmin(admin.ModelAdmin):
    list_filter = ('brand',)
    list_display = ('product_name', 'api_key', 'nm_id', 'brand')


@admin.register(SaleReport)
class SaleReportAdmin(admin.ModelAdmin):
    search_fields = ['owner__email']
    list_display = ('owner', 'realizationreport_id', 'create_dt', 'week_num')


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_filter = ('subscription_type', )
    search_fields = ['user__email']
    list_display = ('__str__', 'subscription_type', 'subscribed_from', 'subscribed_to', 'is_active')

    def is_active(self, obj):
        result = True if obj.subscribed_to >= datetime.now() else False
        return result

    is_active.short_description = "Активна ли подписка"
