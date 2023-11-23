from django.shortcuts import redirect


class RedirectUnauthenticatedToDemo:

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('reports:demo_dashboard_main')

        return super().dispatch(request, *args, **kwargs)
