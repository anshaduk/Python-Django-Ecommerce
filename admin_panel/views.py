from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from store.models import Product
from category.models import Category
from orders.models import Order,OrderProduct,Payment
from accounts.models import Account
from admin_panel.forms import ProductUpdateForm,CategoryUpdateForm,OrderStatusUpdateForm
# Create your views here.
def super_admin(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(super_admin)
def admin_panel(request):
    return render(request,"admin_template/admin_panel.html")

def products(request):
    products = Product.objects.all().order_by("id")
    context = {
        'products' : products,
    }
    return render(request,"admin_template/products.html",context)

def add_product(request):
    if request.method == "POST":
        form = ProductUpdateForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request,'Product added successfully.')
            return redirect("admin_product")
    else:
        form = ProductUpdateForm()
    context = {
        'form':form,
    }    
    return render(request,"admin_template/add_product.html",context)

def edit_product(request,id):
    product = get_object_or_404(Product, id=id)

    if request.method == "POST":
        form = ProductUpdateForm(request.POST,request.FILES,instance=product)
        if form.is_valid():
            form.save()
            messages.success(request,'Product edited successfully.')
            return redirect("admin_product")
    else:
        form = ProductUpdateForm(instance=product)
    context = {
        "form" : form,
    }
    return render(request,"admin_template/add_product.html",context)

def delete_product(request,id):
    product = Product.objects.get(id=id)
    product.delete()
    messages.success(request,'Product deleted successfully.')
    return redirect('admin_product')

def category(request):
    categories = Category.objects.all().order_by('id')
    context = {
        'categories' : categories
    }

    return render(request,'admin_template/category.html',context)

def add_category(request):
    if request.method == 'POST':
        form = CategoryUpdateForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request,'Category added successfully.')
            return redirect('admin_category')
    else:
        form = CategoryUpdateForm()
    context = {
        'form' : form,
    }
    return render(request,'admin_template/add_category.html',context)

def edit_category(request,slug):
    category = Category.objects.get(slug=slug)

    if request.method == "POST":
        form = CategoryUpdateForm(request.POST,request.FILES,instance=category)
        if form.is_valid():
            form.save()
            messages.success(request,'Category edited successfully.')
            return redirect('admin_category')
    else:
        form = CategoryUpdateForm(instance=category)
    
    context = {
        'form' : form,
    }
    return render(request,'admin_template/add_category.html',context)

def delete_category(request,slug):
    category = Category.objects.get(slug=slug)
    category.delete()
    messages.success(request,'Category deleted successfully.')
    return redirect('admin_category')

def orders(request):
    orders = Order.objects.all().order_by('-created_at')
    context = {
        'orders' : orders,
    }
    return render(request,'admin_template/orders.html',context)

def orderdetails(request,id):
    order = Order.objects.get(id=id)
    details = OrderProduct.objects.filter(order=order)
    print(f"Details: {details}")
    ordered_products = OrderProduct.objects.filter(order_id=order.id)
    subtotal = 0
    for i in ordered_products:
        subtotal += i.product_price * i.quantity
    context = {
        "details" : details,
        "order"   : order,
        'ordered_products' : ordered_products,
        'subtotal' : subtotal,
        }
    
    return render(request,'admin_template/orderdetails.html',context)

def update_order_status(request,id):
    order = get_object_or_404(Order,id=id)
    
    if request.method == "POST":
        form = OrderStatusUpdateForm(request.POST,instance=order)
        if form.is_valid():
            form.save()
            return redirect('orderdetails',id=id)
    else:
        form = OrderStatusUpdateForm(instance=order)
    context = {
        'form' : form,
        'order' : order,
            
    }
    return render(request,'admin_template/update_order_status.html',context)

 