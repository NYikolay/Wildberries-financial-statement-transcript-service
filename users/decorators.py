from django.shortcuts import render, redirect


def redirect_authenticated_user(func):
    def wrapper(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('users:profile')
        return func(self, request, *args, **kwargs)
    return wrapper
