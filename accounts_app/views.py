from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import *
# Create your views here.
@login_required
def profile_view(request):
    """فقط رندر کردن template - تمام دیتا با API می‌آید"""
    return render(request, 'accounts_app/profile.html')


def about_us_view(request):
    """
    نمایش صفحه درباره ما
    """
    about_info = AboutUs.objects.filter(is_active=True).first()

    context = {
        "about_info": about_info,
    }
    return render(request, 'accounts_app/AboutUs.html', context)