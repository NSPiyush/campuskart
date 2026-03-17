from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def seller_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        try:
            if request.user.profile.user_type != 'senior':
                messages.error(request, 'You need to be a senior (seller) to access this page.')
                return redirect('dashboard')
        except:
            return redirect('login')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def buyer_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        try:
            if request.user.profile.user_type != 'junior':
                messages.error(request, 'You need to be a junior (buyer) to access this page.')
                return redirect('dashboard')
        except:
            return redirect('login')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view