from datetime import datetime

from django.contrib import admin

from users.models import (User, WBApiKey, SaleObject,
                          ClientUniqueProduct, NetCost, SaleReport, TaxRate,
                          IncorrectReport, UnloadedReports, UserSubscription, UserDiscount, Order, Promocode)


admin.site.register(NetCost)
admin.site.register(TaxRate)
admin.site.register(IncorrectReport)
admin.site.register(UnloadedReports)
admin.site.register(UserDiscount)
admin.site.register(Promocode)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_filter = ('is_active', 'date_joined')
    search_fields = ['email']
    list_display = ('email', 'date_joined', 'phone', 'is_subscribed', 'is_active')
    readonly_fields = ['email', 'date_joined', 'phone', 'is_subscribed', 'password']


@admin.register(SaleObject)
class SaleObjectAdmin(admin.ModelAdmin):
    list_display = ('id', '__str__')
    search_fields = ('nm_id', 'barcode', 'realizationreport_id', 'owner__email')

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(
            set([field.name for field in self.opts.local_fields] +
                [field.name for field in self.opts.local_many_to_many]))

        if 'is_submitted' in readonly_fields:
            readonly_fields.remove('is_submitted')

        return readonly_fields


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_filter = ('status', 'created_at')
    list_display = ('user', 'status', 'paid_sum', 'created_at')


@admin.register(WBApiKey)
class WBApiKeyAdmin(admin.ModelAdmin):
    search_fields = ('user__email', )
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
    readonly_fields = ['api_key']


@admin.register(ClientUniqueProduct)
class ClientUniqueProductAdmin(admin.ModelAdmin):
    list_filter = ('brand',)
    list_display = ('product_name', 'api_key', 'nm_id', 'brand')
    search_fields = ('nm_id', 'product_name', 'brand')


@admin.register(SaleReport)
class SaleReportAdmin(admin.ModelAdmin):
    search_fields = ['owner__email']
    list_display = ('owner', 'realizationreport_id', 'create_dt', 'week_num')

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(
            set([field.name for field in self.opts.local_fields] +
                [field.name for field in self.opts.local_many_to_many]))

        if 'is_submitted' in readonly_fields:
            readonly_fields.remove('is_submitted')

        return readonly_fields


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_filter = ('subscription_type', )
    search_fields = ['user__email']
    list_display = ('__str__', 'subscription_type', 'subscribed_from', 'subscribed_to', 'is_active')

    def is_active(self, obj):
        result = 'Активна' if obj.subscribed_to >= datetime.now() else 'Не активна'
        return result

    is_active.short_description = "Активна ли подписка"
