from django.shortcuts import render,redirect
from . forms import RegistrationForm
from . models import Account
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

# def login(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         print(email)
#         password = request.POST.get('password')
#         print(password)
#         user = auth.authenticate(request,email=email,password=password)
#         print(user,'iiiiiiiiiiiiiiiiiii')

#         if user is not None:
#             auth.login(request,user)
#             return redirect('index')
#             # print('hello')    
#         else:
#             messages.error(request,"Invalid login credentials")
#             return redirect('login')
#     return render(request,'accounts/login.html')

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)    
                login(request,user)
                return redirect('index')
            else:
                messages.error(request,"Invalid login credentials")    
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
        messages.success(request,'Congratulations...! Your account is activated.')
        return redirect('login')
    else:
        messages.error(request,'Invalid activation link')
        return redirect('register')
    return HttpResponse('ok')