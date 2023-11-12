from users.models import ClientUniqueProduct, SaleReport, TaxRate, IncorrectReport
from django.db.models import Q, Count, Exists
from django.urls import reverse


def user_additional_data(request):
    data = {}

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

            is_filled_net_cost = not ClientUniqueProduct.objects.annotate(net_cost_count=Count('cost_prices')).filter(
                net_cost_count=0).exists()

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

        data['current_api_key'] = current_api_key
        data['api_keys'] = api_keys

    return data


def current_path(request):
    profile_urls = [
        reverse("users:change_password"),
        reverse("users:profile_subscriptions"),
        reverse("users:register"), reverse("users:password_reset"), reverse("users:password_reset_done"),
        reverse("users:login"), reverse("users:email_confirmation_info"), reverse("support:support"),
        '/password-reset/confirm/'
    ]

    data_urls = [
        reverse("reports:reports_list"), reverse("users:create_api_key"), reverse("users:companies_list"),
        '/profile/api-key/edit/', reverse("users:profile_taxes"), reverse("users:costs_list"), '/product/',
        reverse("users:empty_products")
    ]

    return {
        "is_profile_url": request.path in profile_urls or any(list(map(lambda url: url in request.path, profile_urls))),
        "is_data_url": request.path in data_urls or any(list(map(lambda url: url in request.path, data_urls))),
        "is_dashboard_url": False
    }
