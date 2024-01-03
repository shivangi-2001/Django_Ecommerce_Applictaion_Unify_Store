from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
import uuid

USER = get_user_model()

class Collection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, auto_created=True)
    title = models.CharField(max_length= 255, blank=False, unique=True)

    def __str__(self):
        return self.title

class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True)
    title  = models.CharField(max_length=255, blank=False)
    description= models.TextField(blank=False)
    image = models.ImageField(upload_to='', null=True)
    unit_price = models.DecimalField(max_digits=7, decimal_places=3, blank=False)
    inventory= models.PositiveIntegerField(default=0, blank=False)
    last_update =  models.DateTimeField(auto_now_add=True, blank=False)
    collection = models.ForeignKey(Collection, on_delete=models.SET_NULL, null=True, to_field='id')
    slug =  models.SlugField()

    class Meta:
        verbose_name  = 'Product'
        

class Cart(models.Model):
    user = models.ForeignKey(USER, on_delete=models.CASCADE, related_name='user', null=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product')
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_id')
    quantity = models.PositiveIntegerField(default=1)