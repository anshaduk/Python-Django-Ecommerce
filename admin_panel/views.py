from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test,login_required
from store.models import Product
from category.models import Category
from orders.models import Order,OrderProduct,Payment
from accounts.models import Account,UserProfile
from admin_panel.forms import ProductUpdateForm,CategoryUpdateForm,OrderStatusUpdateForm
from django.contrib.auth import logout,login
from django.contrib import messages, auth

# Create your views here.
def super_admin(user):
    return user.is_authenticated and user.is_staff
       

@user_passes_test(super_admin)
def admin_panel(request):
    return render(request,"admin_template/admin_panel.html")

@user_passes_test(super_admin)
def products(request):
    products = Product.objects.all().order_by("id")
    context = {
        'products' : products,
    }
    return render(request,"admin_template/products.html",context)

@user_passes_test(super_admin)
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

@user_passes_test(super_admin)
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

@user_passes_test(super_admin)
def delete_product(request,id):
    product = Product.objects.get(id=id)
    product.delete()
    messages.success(request,'Product deleted successfully.')
    return redirect('admin_product')

@user_passes_test(super_admin)
def category(request):
    categories = Category.objects.all().order_by('id')
    context = {
        'categories' : categories
    }

    return render(request,'admin_template/category.html',context)

@user_passes_test(super_admin)
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

@user_passes_test(super_admin)
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

@user_passes_test(super_admin)
def delete_category(request,slug):
    category = Category.objects.get(slug=slug)
    category.delete()
    messages.success(request,'Category deleted successfully.')
    return redirect('admin_category')

@user_passes_test(super_admin)
def orders(request):
    orders = Order.objects.all().order_by('-created_at')
    context = {
        'orders' : orders,
    }
    return render(request,'admin_template/orders.html',context)

@user_passes_test(super_admin)
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

@user_passes_test(super_admin)
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

@user_passes_test(super_admin)
def users(request):
    
    users = Account.objects.exclude(is_admin=True).exclude(is_superadmin=True).order_by('id')
    context = {
       'users' : users, 
    }
    return render(request,'admin_template/users.html',context)

@user_passes_test(super_admin)
def blockusers(request,id):
    user_to_block = Account.objects.get(id=id)

    if user_to_block.is_superadmin:
        messages.error(request,"Cannot block super admin.")
    elif user_to_block.is_staff and user_to_block == request.user:
        messages.error(request,"Cannot block yourself.")
    else:
        if user_to_block.is_blocked:
            user_to_block.is_blocked = False
            messages.success(request,f"{user_to_block.get_full_name()} has been unblocked...!")
            user_to_block.save()
        else:
            user_to_block.is_blocked = True
            messages.success(request,f"{user_to_block.get_full_name()} has been blocked...!")
            user_to_block.save()
    return redirect('admin_users')

@user_passes_test(super_admin)
def userprofile(request,id):
    usr = Account.objects.get(pk=id)
    user =  UserProfile.objects.get(user=usr)
    print(user)
    print(user.user.first_name)
    print(user.user.email)
    print(user.full_address())
    context = {
        'user' : user,
    }
    return render(request,'admin_template/users_profile.html',context)

def toggle_admin(request,id):
    user_to_toggle = Account.objects.get(id=id)

    # Super admin cannot toggle own admin status
    if user_to_toggle == request.user:
        messages.error(request,"Cannot change your own admin status.")
    else:
        user_to_toggle.is_staff = not user_to_toggle.is_staff
        user_to_toggle.save()

        action = "added" if user_to_toggle.is_staff else "removed"
        messages.success(request,f"{user_to_toggle.get_full_name()} has been {action} as an Admin...")
    return redirect('userprofile',id=user_to_toggle.id)

@login_required(login_url="login")
def admin_logout(request):
    auth.logout(request)
    messages.success(request, "you are logout")
    return redirect("login")