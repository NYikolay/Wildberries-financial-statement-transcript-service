from users.models import WBApiKey, ClientUniqueProduct, SaleReport


def current_user_api_key(request):
    if request.user.is_authenticated:
        return {'current_api_key': request.user.keys.filter(is_current=True).first()}
    return {}


def user_last_report_date(request):
    if request.user.is_authenticated and request.user.keys.filter(is_current=True).exists():
        context = {
            'last_report_date': SaleReport.objects.filter(
                api_key__is_current=True, api_key__user=request.user
            ).values_list('create_dt', flat=True).order_by('-create_dt').first(),
        }
        return context
    return {}


def user_product_article(request):
    if request.user.is_authenticated and request.user.keys.filter(is_current=True).exists():
        context = {
            'product_article': ClientUniqueProduct.objects.filter(
                api_key__is_current=True, api_key__user=request.user
            ).order_by('brand', 'nm_id').values_list('nm_id', flat=True)[:1].first()
        }
        return context
    return {}
