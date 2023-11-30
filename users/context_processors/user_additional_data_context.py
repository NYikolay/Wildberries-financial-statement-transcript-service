from users.models import ClientUniqueProduct, SaleReport, TaxRate, IncorrectReport, SaleObject
from django.db.models import Q, Count, Exists, ExpressionWrapper, BooleanField, Case, When, IntegerField
from django.urls import reverse


def user_additional_data(request):
    data = {}
    current_url = request.resolver_match.view_name
    dashboard_urls = [
        "reports:dashboard_main",
        "reports:dashboard_by_barcode",
        "reports:dashboard_abc_xyz"
    ]

    if request.user.is_authenticated:
        current_api_key = request.user.keys.filter(is_current=True).first()
        api_keys = request.user.keys.values("name", "id", "is_current").order_by(
            '-is_current', '-last_reports_update'
        )

        if current_api_key:
            is_filled_report_data = not current_api_key.api_key_reports.filter(
                Q(cost_paid_acceptance__isnull=True) |
                Q(other_deductions__isnull=True) |
                Q(storage_cost__isnull=True)
            ).exists()

            is_filled_report_costs = not current_api_key.api_key_reports.filter(
                Q(supplier_costs__isnull=True)
            ).exists()

            is_filled_net_cost = all(ClientUniqueProduct.objects.filter(
                api_key=current_api_key
            ).annotate(
                has_net_cost=ExpressionWrapper(Q(cost_prices__isnull=False), output_field=BooleanField())
            ).distinct().values_list('has_net_cost', flat=True))

            is_filled_taxes = current_api_key.taxes.filter(api_key=current_api_key).exists()

            is_incorrect_reports = IncorrectReport.objects.filter(api_key=current_api_key).exists()

            product_article = ClientUniqueProduct.objects.filter(
                api_key=current_api_key).values_list('nm_id', flat=True).order_by('brand', 'nm_id').first()

            data['is_filled_report_data'] = is_filled_report_data
            data['is_filled_report_costs'] = is_filled_report_costs
            data['is_filled_net_cost'] = is_filled_net_cost
            data['is_filled_taxes'] = is_filled_taxes
            data['product_article'] = product_article
            data['is_incorrect_reports'] = is_incorrect_reports

            if current_url in dashboard_urls:
                random_product_barcode = SaleObject.objects.filter(
                    api_key=current_api_key
                ).values('barcode').order_by('barcode').first()

                data['random_product_barcode'] = random_product_barcode['barcode']

        data['current_api_key'] = current_api_key
        data['api_keys'] = api_keys

    return data


def current_path(request):
    current_url = request.resolver_match.view_name

    profile_urls = [
        "users:change_password",
        "users:profile_subscriptions",
        "users:register", "users:password_reset", "users:password_reset_done",
        "users:login", "users:email_confirmation_info", "support:support",
        "users:password_reset_confirm"
    ]

    data_urls = [
        "reports:reports_list", "users:create_api_key", "users:companies_list",
        "users:api_key_edit", "users:profile_taxes", "users:costs_list", "users:product_detail",
        "users:empty_products"
    ]

    dashboard_urls = [
        "reports:dashboard_main", "reports:demo_dashboard_main",
        "reports:dashboard_by_barcode", "reports:demo_dashboard_by_barcode", 'reports:dashboard_abc_xyz',
        'reports:demo_dashboard_abc_xyz'
    ]

    return {
        "is_profile_url": current_url in profile_urls,
        "is_data_url": current_url in data_urls,
        "is_dashboard_url": current_url in dashboard_urls
    }
