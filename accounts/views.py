from django.shortcuts import render,redirect,get_object_or_404
from . forms import RegistrationForm,UserForm,UserProfileForm
from . models import Account,UserProfile
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate  , login , logout
from .forms import LoginForm
from django.http import HttpResponse

#Verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from carts.views import _cart_id
from carts.models import Cart,CartItem

from orders.models import Order


# Create your views here.


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split('@')[0]
            user = Account.objects.create_user(first_name=first_name,last_name=last_name,email=email,username=username,password=password)
            user.phone_number = phone_number
            user.save()

            #user profile creation                     
            profile  = UserProfile.objects.create(user=user)
            profile.save()


            #user activation
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('accounts/account_verification_email.html',
            {
                'user' : user,
                'domain' : current_site,
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                'token' : default_token_generator.make_token(user),
            },
            )
            to_email = email
            sent_email = EmailMessage(mail_subject,message,to=[to_email])
            sent_email.send()

            # messages.success(request,'Thank you for registering with us. We have sent you a verification email to your email address.please verify it.')
            return redirect('/accounts/login/?command=verification&email='+email)
    else:
        form = RegistrationForm()
    context = {
        'form' : form,
    }
    return render(request,'accounts/register.html',context)



def user_login(request):
    if request.method == 'POST':
        try:
            form = LoginForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data['email']
                password = form.cleaned_data['password']
                users = Account.objects.get(email=email)
                # Authenticate user 
                user = authenticate(request, email=email, password=password)

                if user is not None:  
                     try:
                         cart = Cart.objects.get(cart_id=_cart_id(request)) 
                         is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                         if is_cart_item_exists:
                             cart_item = CartItem.objects.filter(cart=cart)

                             for item in cart_item:
                                 item.user = user
                                 item.save()
                     except Cart.DoesNotExist:
                         pass  
                login(request, user)    
                messages.success(request,'You are now logged in.')
                return redirect('index')
                
            #Error Password entered check
            if not users.check_password(password):
                messages.error(request,"Inv alid Password...!")
                return redirect('login')
            
            # if not user.check_email(email):
            #     messages.error(request,"Invalid Password...!")
            #     return redirect('login')
        
        except Account.DoesNotExist: 
                messages.error(request,"No user found with this email...!")    
                return redirect('login')
            
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})






@login_required(login_url = 'login')
def user_logout(request):
    logout(request)
    messages.success(request,'You are logged out')
    return redirect('login')


def activate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user,token):
        user.is_active = True
        user.save()
        # messages.success(request,'Congratulations...! Your account is activated.')
        
        # user = authenticate(request, email=user.email, password=user.password)
        login(request, user) 
        return redirect('index')
    else:
        messages.error(request,'Invalid activation link')
        return redirect('register')

@login_required(login_url = 'login')
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id,is_ordered=True)
    orders_count = orders.count()
    userprofile = get_object_or_404(UserProfile,user=request.user)
    context = {
        'orders_count' : orders_count,
        'userprofile'   : userprofile,
    }
    return render(request,'accounts/dashboard.html',context)

def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            #Reset Password email
            current_site = get_current_site(request)
            mail_subject = 'Reset Your Password'
            message = render_to_string('accounts/reset_password_email.html',
            {
                'user' : user,
                'domain' : current_site,
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                'token' : default_token_generator.make_token(user),
            },
            )
            to_email = email
            sent_email = EmailMessage(mail_subject,message,to=[to_email])
            sent_email.send()

            messages.success(request,'Password reset email has been sent to your email address.')
            return redirect('login')

        else:
            messages.error(request,'Account does not exist!')
            return redirect('forgotPassword')
    return render(request,'accounts/forgotPassword.html')

def resetpassword_validate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('resetPassword')
    else:
        messages.error(request, 'This link has been expired!')
        return redirect('login')

def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password) #Hashing password into Data Base
            user.save()
            messages.success(request,'Password reset successful')
            return redirect('login')
        else:
            messages.error(request,'Password do not match!')
            return redirect('resetPassword')
    else:
        return render(request,'accounts/resetPassword.html')


@login_required(login_url='login')
def editprofile(request):
 
    userprofile = get_object_or_404(UserProfile,user=request.user)
   
    if request.method == "POST":
        user_form = UserForm(request.POST,instance=request.user)
        profile_form = UserProfileForm(request.POST,request.FILES,instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            if user_form is None:
                user_form = profile_form.save(commit=False)
                user_form.user = request.user
            profile_form.save()
            messages.success(request,'Your profile has been updated')
            return redirect('editprofile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)   
        
    

    context = {
        'user_form' : user_form,
        'profile_form' : profile_form,
        'userprofile' : userprofile,
    }
    return render(request,'accounts/editprofile.html',context)

def my_orders(request):
    orders = Order.objects.filter(user=request.user,is_ordered=True).order_by('-created_at')
    context = {
      'orders' : orders,  
    }
    return render(request,'accounts/my_orders.html',context)


@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.objects.get(username__exact=request.user.username)
        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                messages.success(request,'Password updated successfully...')
                return redirect('change_password')
            else:
                messages.error(request,'Please enter valid current password')
                return redirect('change_password')
        else:
            messages.error(request,'Password does not match!')
            return redirect('change_password')
    return render(request,'accounts/change_password.html')