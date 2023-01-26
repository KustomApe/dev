from django.contrib import admin

# Register your models here.

from . import models
admin.site.register(models.Category)
admin.site.register(models.Item)
admin.site.register(models.ItemsInCart)
admin.site.register(models.Purchase)
admin.site.register(models.PurchaseDetail)