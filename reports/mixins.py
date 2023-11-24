from django.shortcuts import redirect


class RedirectUnauthenticatedToDemo:
    reverse_redirect_demo_url = None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(self.reverse_redirect_demo_url)

        return super().dispatch(request, *args, **kwargs)
