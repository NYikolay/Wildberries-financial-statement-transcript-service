from django.contrib import admin

from users.models import User, WBApiKey, SaleObject, ClientUniqueProduct, NetCost, SaleReport, TaxRate, IncorrectReport

admin.site.register(WBApiKey)
admin.site.register(SaleObject)
admin.site.register(ClientUniqueProduct)
admin.site.register(NetCost)
admin.site.register(SaleReport)
admin.site.register(TaxRate)
admin.site.register(IncorrectReport)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_filter = ('is_active', )
