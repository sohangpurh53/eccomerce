from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User,  Product, ShippingAddress, Review, AboutUs, ProductImage
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

class SellerRegistrationForm(UserCreationForm):
    company_name = forms.CharField(max_length=200)
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ('username','email' ,'password1', 'password2', 'company_name')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
        self.fields['username'].help_text = None


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'shipping_fee' ,'initial_stock', 'stock' ,'category']


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image']
        

class SignupForm(UserCreationForm):
    email = forms.EmailField()
    mobile_no = forms.IntegerField()
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'mobile_no','password1', 'password2']
    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['password1'].help_text = None
            self.fields['password2'].help_text = None
            self.fields['username'].help_text = None

    def save(self, commit=True):
            user = super().save(commit=False)
            if commit:
                user.save()

                # Send an email to the new user
                subject = 'Welcome to our platform'
                message = 'Thank you for signing up!'
                from_email = settings.EMAIL_HOST_USER
                recipient_list = [user.email]
                html_message = render_to_string('signupemail.html')
                send_mail(subject, message, from_email, recipient_list, html_message=html_message)

            return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)



class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = ['address','city', 'state', 'postal_code', 'country']



class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']



class AboutUsForm(forms.ModelForm):
    class Meta:
        model = AboutUs
        fields = ['description']

