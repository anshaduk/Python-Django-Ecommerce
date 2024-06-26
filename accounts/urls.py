from django.urls import path
from .import views
urlpatterns = [
    path('register/',views.register,name="register"),
    path('login/',views.user_login,name='login'),
    path('logout/',views.user_logout,name='logout'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('',views.dashboard,name='dashboard'),

    path("activate/<uidb64>/<token>/", views.activate, name="activate"),
    path('forgotPassword/',views.forgotPassword,name='forgotPassword'),
    path('resetpassword_validate/<uidb64>/<token>/',views.resetpassword_validate,name='resetpassword_validate'),
    path('resetPassword/',views.resetPassword,name='resetPassword'),
    
    path('editprofile/',views.editprofile,name='editprofile'),
    path('my_orders/',views.my_orders,name='my_orders'),
    path('change_password/',views.change_password,name='change_password'),
]