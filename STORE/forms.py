from django import forms
from .models import Product, CartItem


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

class CartItemForm(forms.ModelForm):
    class Meta:
        model = CartItem
        fields = '__all__'
