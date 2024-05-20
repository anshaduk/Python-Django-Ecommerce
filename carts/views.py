from django.shortcuts import render,redirect,get_object_or_404
from store.models import Product
from carts.models import Cart
from carts.models import CartItem
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib import messages


# Create your views here.

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request,product_id):
    current_user = request.user
    if current_user.is_authenticated and current_user.is_superadmin:
        messages.warning(request,"Super admins cannot add items to the cart.")
        return redirect("store")
    product = Product.objects.get(id=product_id)# get the product

    # if the user is authenticated
    if current_user.is_authenticated:
        try:
            #get the cart using the cart_id present in the session
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
            cart.save()
        is_cart_item_exists = CartItem.objects.filter(
            product = product,user=current_user
        ).exists()

        if is_cart_item_exists:
            cart_items = CartItem.objects.filter(product=product,user=current_user)
            for item in cart_items:
                item.quantity += 1
                item.save()
        
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                user = current_user,
                cart = cart,
        )
            cart_item.save()
        return redirect('cart')

    # if the user is not authenticated
    else:
        try:
            cart = Cart.objects.get(cart_id = _cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id = _cart_id(request))
        cart.save()

        is_cart_item_exists = CartItem.objects.filter(
            product = product,cart = cart
        ).exists()

        if is_cart_item_exists:
            cart_items = CartItem.objects.filter(product = product,cart=cart)
            for item in cart_items:
                item.quantity += 1
                item.save()

        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                cart = cart,
            )
            cart_item.save()
        return redirect("cart")
        
            
        
    # return HttpResponse(cart_item.quantity)    
    # exit()
    
def cart(request, total=0, quantity=0, cart_items = None):  
    try:
        tax = 0
        grand_total = 0
        cart_count = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user,is_active=True)
            cart_count = cart_items.count()
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart,is_active=True)
            cart_count = cart_items.count()

        for cart_item in cart_items:
            total += (cart_item.product.price*cart_item.quantity)
            quantity += cart_item.quantity

        # 5% of tax    
        tax = (5 * total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass #just ignore
    context = {
        'total' : total,
        'quantity' : quantity,
        'cart_items' : cart_items,
        'tax'       : tax,
        'grand_total' : grand_total,
        'cart_count' : cart_count,
    }        
    return render(request,'store/cart.html',context)     

def remove_cart(request,product_id,cart_item_id): 
    product = get_object_or_404(Product,id=product_id)
    try:
        if request.user.is_authenticated:   
            cart_item = CartItem.objects.get(product=product,user=request.user,id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product,cart=cart,id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else: 
            cart_item.delete()
    except:
        pass
    return redirect('cart')

def remove_cart_item(request,product_id,cart_item_id):
    product = get_object_or_404(Product,id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product,user=request.user,id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=product,cart=cart,id=cart_item_id)
    cart_item.delete()
    return redirect('cart')

@login_required(login_url='login')
def checkout(request,total=0, quantity=0, cart_items = None):
    try:
        tax = 0
        grand_total = 0
        cart_count = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user,is_active=True)
            cart_count = cart_items.count()
        else:   
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart,is_active=True)
            cart_count = cart_items.count()

        for cart_item in cart_items:
            total += (cart_item.product.price*cart_item.quantity)
            quantity += cart_item.quantity

        # 5% of tax    
        tax = (2 * total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass #just ignore

    context = {
        'total' : total,
        'quantity' : quantity,
        'cart_items' : cart_items,
        'tax'       : tax,
        'grand_total' : grand_total,
        'cart_count' : cart_count,
    }
    return render(request,'store/checkout.html',context)

  