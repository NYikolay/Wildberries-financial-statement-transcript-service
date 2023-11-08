from reports.models import InfoTypes, GeneralInformationObj
from users.models import ClientUniqueProduct, SaleReport
from django.urls import reverse


def user_additional_data(request):
    data = {}

    if request.user.is_authenticated:
        current_api_key = request.user.keys.filter(is_current=True).first()
        data['current_api_key'] = current_api_key
        data['api_keys'] = request.user.keys.values(
            "name", "id", "is_current"
        ).order_by('-is_current', '-last_reports_update')

        if current_api_key:
            data['product_article'] = ClientUniqueProduct.objects.filter(
                api_key=current_api_key
            ).values_list('nm_id', flat=True).order_by('brand', 'nm_id').first()

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


def user_last_report_date(request):
    if request.user.is_authenticated and request.user.keys.filter(is_current=True).exists():
        context = {
            'last_report_date': SaleReport.objects.filter(
                api_key__is_current=True, api_key__user=request.user
            ).values_list('create_dt', flat=True).order_by('-create_dt').first(),
        }
        return context
    return {}
