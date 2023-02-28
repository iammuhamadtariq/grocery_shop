from django import forms
from .models.product import Product
from .models.category import Category
from .models.customer import Customer


class CreateProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ('product_name','product_price','product_catagory','product_description','product_image')

        widget = {

            'product_name': forms.TextInput(attrs={'class': 'form-control'}),
            'product_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'product_catagory': forms.Select(attrs={'class': 'form-control'}),
            'product_description': forms.TextInput(attrs={'class': 'form-control'}),
            'product_image': forms.FileInput(attrs={'class': 'form-control'}),
            
        }

class CreateCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('category_name',)
        widget = {
            'category_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ('customer_name','customer_email','customer_password','customer_type')
        widgets = {'customer_type': forms.HiddenInput()}

class LoginForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ('customer_email','customer_password')
        