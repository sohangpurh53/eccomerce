from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User,  Product, ShippingAddress, Review
from django.contrib.auth.forms import AuthenticationForm

class SellerRegistrationForm(UserCreationForm):
    company_name = forms.CharField(max_length=200)

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'company_name')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
        self.fields['username'].help_text = None

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'initial_stock', 'category', 'image']

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
   