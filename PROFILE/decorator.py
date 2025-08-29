from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

def anonymous_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('index')
        return view_func(request, *args, **kwargs)
    return wrapper

