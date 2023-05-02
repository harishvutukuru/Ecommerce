from django import forms
from .models import Product, Order, Purchase, Sale, ecom, Category, SubCategory,UserProfile,cart
from django.contrib.auth.models import User


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['name', 'order_quantity']

class cartForm(forms.ModelForm):
    class Meta:
        model = cart
        fields = ['product', 'quantity']

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        users = UserProfile.objects.filter(user_role='vendor')
        if users:
            self.fields['vendor'].queryset = users


class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = '__all__'


class ecomForm(forms.ModelForm):
    class Meta:
        model = ecom
        fields = '__all__'


class UserForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('username', 'password', 'email', 'first_name', 'last_name', 'user_role')


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'


class SubCategoryForm(forms.ModelForm):
    class Meta:
        model = SubCategory
        fields = '__all__'

class OrderFormStatus(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['name', 'order_status']

class UserLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs=dict(max_length=25,
                                                             placeholder='Enter Username')),
                           error_messages={'required': 'Username is required!'})
    password = forms.CharField(widget=forms.PasswordInput(attrs=dict(
    required=True,
    max_length=30,
    render_value=False,
    placeholder='Password'),
    ),
    label=("Password"),
    error_messages={'required': 'Password is required!'})

    class Meta:
        fields = ('username', 'password')