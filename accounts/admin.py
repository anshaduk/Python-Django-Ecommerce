from django.contrib import admin
from . models import Account
# Register your models here.


class AccountAdmin(admin.ModelAdmin):
    list_display = ('email','first_name','last_name','username','last_login','date_joined','is_active')

admin.site.register(Account)

