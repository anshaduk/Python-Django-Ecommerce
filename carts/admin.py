from django.contrib import admin
from . models import Cart
from .models import CartItem

# # Register your models here.
class CartAdmin(admin.ModelAdmin):
    list_display = ('date_added',)


class CartItemAdmin(admin.ModelAdmin):
    list_display = ('product','cart','quantity','is_active')

admin.site.register(Cart,CartAdmin)
admin.site.register(CartItem)
