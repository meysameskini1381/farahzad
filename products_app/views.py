from .models import *
from django.shortcuts import render

def product_by_category(request, category_slug):

    return render(
        request,
        "product_app/product_list.html",
        {
            "category_slug": category_slug
        }
    )

def product_detail(request, product_slug):
    return render(
        request,
        "product_app/product-detail.html",
        {
            "product_slug": product_slug
        }
    )
