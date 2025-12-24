from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def profile_view(request):
    """فقط رندر کردن template - تمام دیتا با API می‌آید"""
    return render(request, 'accounts_app/profile.html')