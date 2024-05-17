from django.urls import path
from carts import views

urlpatterns = [
    path('',views.cart,name='cart'),
]