from django.contrib import admin
from .models import *

admin.site.register(Category)
admin.site.register(ProductGallery)
admin.site.register(ProductFeature)
admin.site.register(Product)
admin.site.register(ProductComment)

# Register your models here.
