from django.http import HttpResponseForbidden

from config.settings.base import PROMETHEUS_IP


class MetricsMiddleware:
    ALLOWED_IPS = [PROMETHEUS_IP]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/metrics'):
            remote_ip = request.META.get('REMOTE_ADDR')
            if remote_ip not in self.ALLOWED_IPS:
                return HttpResponseForbidden()

        response = self.get_response(request)

        return response
