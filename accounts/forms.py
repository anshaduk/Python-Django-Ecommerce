from typing import Any, Mapping
from django import forms
import re
from django.core.exceptions import ValidationError,FieldError
from django.contrib.auth.password_validation import(
    MinimumLengthValidator,
    CommonPasswordValidator,
    NumericPasswordValidator,
)
from django.core.files.base import File
from django.db.models.base import Model
from django.forms.utils import ErrorList
from . models import Account
from .models import UserProfile



class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'Enter Password',
        'class' : 'form-control',

    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder' : 'Confirm Password'
    }))
    class Meta:
        model = Account
        fields = ['first_name','last_name','phone_number','email','password'] 

    def __init__(self,*args,**kwargs):
        super(RegistrationForm,self).__init__(*args,**kwargs)
        self.fields['first_name'].widget.attrs['placeholder']='Enter First Name'
        self.fields['last_name'].widget.attrs['placeholder']='Enter Last Name'
        self.fields['phone_number'].widget.attrs['placeholder']='Enter Phone Number'
        self.fields['email'].widget.attrs['placeholder']='Enter Email Address'
        for field in self.fields:
            self.fields[field].widget.attrs['class']='form-control'


    def clean_username(self,name,field_name):
        # Check if the username contains only alphabets
        if not re.match("^[a-zA-Z]+$",name):
            raise forms.ValidationError(f"{field_name} should only contain alphabets")
        return name
    
    def clean_password(self):
        password = self.cleaned_data.get('password')

        # Check for minimum length and common passwords
        validators = [
            MinimumLengthValidator(),
            CommonPasswordValidator(),
            NumericPasswordValidator(),
        ]

        errors = []

        for validator in validators:
            try:
                validator.validate(password)
            except ValidationError as e:
                errors.extend(e.error_list)
        
        #Check for the inclusion of special characters,lowercase letters,and uppercase letters
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]',password):
            errors.append(
                ValidationError("Password must contain at least one special character.")
            )

        if not re.search(r"[a-z]",password):
            errors.append(
                ValidationError("Password must contain at least one lowercase letter.")
            )
        
        if not re.search(r"[A-Z]",password):
            errors.append(
                ValidationError("Password must contain at least one uppercase letter.")
            )

        # Your custom password validation goes here.
        # For example, you might want to ensure it doesn't contain the username or other specific rules.

        if errors:
            raise forms.ValidationError(errors)
        

        return password
    
    #Phone_number validation
    # def clean_phone(self):
    #     phone_number = self.cleaned_data.get("phone_number")
    #     z = phonenumbers.parse(phone_number,"SG")
    #     if not phonenumbers.is_valid_number(z):
    #         raise forms.ValidationError("Number not in SG format")
    #     return phone_number
    
    def clean(self):
        cleaned_data = super(RegistrationForm,self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError(
                " Password does not match..!"
            )
        
        cleaned_data['first_name'] = self.clean_username(
            cleaned_data.get("first_name"),"First Name"
        )
        cleaned_data['last_name'] = self.clean_username(
            cleaned_data.get("last_name"),"Last Name"
        )
        return cleaned_data
    

class LoginForm(forms.Form):
    email = forms.EmailField(max_length=150, widget=forms.EmailInput(attrs={
        'placeholder': 'Enter Email',
        'class': 'form-control'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter Password',
        'class': 'form-control'
    }))

class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('first_name','last_name','phone_number')

    def __init__(self,*args,**kwargs):
        super(UserForm,self).__init__(*args,**kwargs) 
        for field in self.fields:
            self.fields[field].widget.attrs['class']='form-control'

class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False, error_messages={'invalid':("Image files only")},widget=forms.FileInput,)
    class Meta:
        model = UserProfile
        fields = ('address_line_1','address_line_2','city','state','country','profile_picture')

    def __init__(self,*args,**kwargs):
        super(UserProfileForm,self).__init__(*args,**kwargs) 
        for field in self.fields:
            self.fields[field].widget.attrs['class']='form-control'