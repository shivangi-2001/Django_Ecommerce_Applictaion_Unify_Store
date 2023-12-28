from django.db import models
import uuid

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