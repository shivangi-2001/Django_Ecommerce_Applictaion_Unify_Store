from rest_framework.serializers import ModelSerializer
from .models import Product, Collection

class ProductSerializer(ModelSerializer):

    class Meta:
        model= Product
        fields = '__all__'
        
        

class CollectionSerializer(ModelSerializer):

    class Meta:
        model= Collection
        fields = '__all__'



