from django.shortcuts import redirect



def not_logged_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(to=("dashboard_urls:dashboard"))
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func
