from django.shortcuts import render


def handler400(request, *args, **kwargs):
    return render(request, 'custom_error_pages/400_page.html', status=400)


def handler403(request, *args, **kwargs):
    return render(request, 'custom_error_pages/403_page.html', status=403)


def handler404(request, *args, **kwargs):
    return render(request, 'custom_error_pages/404_page.html', status=404)


def handler500(request, *args, **kwargs):
    return render(request, 'custom_error_pages/500_page.html', status=500)


def handler502(request, *args, **kwargs):
    return render(request, 'custom_error_pages/502_page.html', status=502)


def handler503(request, *args, **kwargs):
    return render(request, 'custom_error_pages/503_page.html', status=503)
