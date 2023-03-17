from django.contrib import admin

from users.models import (User, WBApiKey, SaleObject,
                          ClientUniqueProduct, NetCost, SaleReport, TaxRate,
                          IncorrectReport, UnloadedReports, UserSubscription, UserDiscount, Order)

admin.site.register(SaleObject)
admin.site.register(NetCost)
admin.site.register(TaxRate)
admin.site.register(IncorrectReport)
admin.site.register(UnloadedReports)
admin.site.register(UserSubscription)
admin.site.register(UserDiscount)
admin.site.register(Order)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_filter = ('is_active', 'date_joined')
    list_display = ('email', 'date_joined')


@admin.register(WBApiKey)
class WBApiKeyAdmin(admin.ModelAdmin):
    list_filter = (
        'last_reports_update',
        'is_wb_data_loaded',
        'is_products_loaded',
        'last_reports_update',
        'is_active_import'
    )
    list_display = ('__str__', 'created_at')


@admin.register(ClientUniqueProduct)
class ClientUniqueProductAdmin(admin.ModelAdmin):
    list_filter = ('brand',)
    list_display = ('product_name', 'api_key', 'nm_id', 'brand')


@admin.register(SaleReport)
class SaleReportAdmin(admin.ModelAdmin):
    list_filter = ('owner',)
    list_display = ('owner', 'realizationreport_id', 'create_dt', 'week_num')
