from django.urls import path
from . import views

urlpatterns = [
    path("admin_panel/",views.admin_panel,name=
         "admin_panel"),
    path('admin_product/',views.products,name='admin_product'),
    path("add_product/",views.add_product,name="add_product"),
    path("<int:id>/edit_product/",views.edit_product,name="edit_product"),
    path("<int:id>/delete_product/",views.delete_product,name='delete_product'),
    path('admin_category/',views.category,name='admin_category'),
    path('add_category/',views.add_category,name='add_category'),
    path('<str:slug>/edit_category/',views.edit_category,name='edit_category'),
    path('<str:slug>/delete_category/',views.delete_category,name='delete_category'),
    path('admin_orders/',views.orders,name='admin_orders'),
    path('<int:id>/orderdetails/',views.orderdetails,name='orderdetails'),
    path('<int:id>/update_status/',views.update_order_status,name='update_order_status'),
    path('admin_users/',views.users,name='admin_users'),
    path('<int:id>/blockusers/',views.blockusers,name='blockusers'),
    path('<int:id>/userprofile/',views.userprofile,name='userprofile'),





    

]