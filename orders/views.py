from django.shortcuts import render,redirect
from django.http import HttpResponse
from carts.models import CartItem
from .forms import OrderForm 
from .models import Order,Payment,OrderProduct
import datetime
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from store.models import Product 
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

# Create your views here.
@csrf_exempt
def payments(request):
    body = json.loads(request.body)
    print("hellloo")
    print(body)
    order = Order.objects.get(
        user = request.user,is_ordered=False,order_number=body['orderID']
    )
    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status' ],
    )
    payment.save()
    order.payment = payment
    order.is_ordered = True
    order.save()
    print(order)

    # move the cart item to the order product table
    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        orderproduct = OrderProduct() 
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True  
        orderproduct.save()
        print(orderproduct)


        #Reduce the quantity of the sold products
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    #Clear cart
    CartItem.objects.filter(user=request.user).delete()

    #send order recieved email to customer
    mail_subject = 'Thank you for your order!'
    message = render_to_string('orders/order_recieved_email.html',
        {
            'user' : request.user,
            'order': order,
        },
        )
    to_email = request.user.email
    sent_email = EmailMessage(mail_subject,message,to=[to_email])
    sent_email.send()

 
    return render(request,'orders/payments.html')

def place_order(request,total=0,quantity=0):
    current_user = request.user

    # if the cart count is less than or equal to 0, than redirect back to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')
    
    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (5*total)/100
    grand_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # store all the billing information inside order table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data.get('first_name')
            data.last_name = form.cleaned_data.get('last_name')
            data.phone = form.cleaned_data.get('phone')
            data.email = form.cleaned_data.get('email')
            data.address_line_1 = form.cleaned_data.get('address_line_1')
            data.address_line_1 = form.cleaned_data.get('address_line_2')
            data.country = form.cleaned_data.get('country')
            data.state = form.cleaned_data.get('state')
            data.city = form.cleaned_data.get('city')
            data.order_note = form.cleaned_data.get('order_note')
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            # Generate oreder number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d  = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user,is_ordered=False,order_number=order_number)
            context = {
                'order' : order,
                'cart_items' : cart_items,
                'total' : total,
                'tax' : tax,
                'grand_total' : grand_total,
            }
            return render(request,'orders/payments.html',context)
    else:
        return redirect('checkout')
    
def order_complete(request):
    return HttpResponse(order_complete)      