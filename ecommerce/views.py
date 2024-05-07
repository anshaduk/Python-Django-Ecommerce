from django.shortcuts import render
from store.models import Product
from category.models import Category

# Create your views here.
def index(request):
    products=Product.objects.all().filter(is_available=True)
    categories=Category.objects.all()
    context={
        'products':products,
        'categories':categories,
    }
    return render(request,'index.html',context)
