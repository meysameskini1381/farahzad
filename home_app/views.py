from django.shortcuts import render
from django.views.generic import TemplateView
from products_app.models import Product,Category
from django.db.models.functions import Random
from django.db.models import Avg, Count



class HomeView(TemplateView):
    template_name = "home_app/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["Category"] = Category.objects.filter(
            is_main=True
        )

        context["Category_parent"] = Category.objects.filter(
            is_main=False
        )
        context['product_vip'] = Product.objects.filter(vip=True)[0:23]

        context['product_featured'] = Product.objects.filter(is_featured=True)[0:6]

        context['list'] = (
            Product.objects
            .filter(is_featured=True, is_active=True)
            .order_by(Random())[:20]
        )

        context['featured_priority'] = Product.objects.filter(
                featured_priority__gte=2,
                featured_priority__lte=5,
                is_active=True
            )

        return context