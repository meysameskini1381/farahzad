from django.shortcuts import render
from .models import *
from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = "home_app/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["vip_products_banner"] = Banner.objects.filter(
            is_active=True,
            position="بنر محصولات vip"
        )

        return context