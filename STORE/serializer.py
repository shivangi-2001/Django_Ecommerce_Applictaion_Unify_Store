from rest_framework import serializers
from .models import Product, Collection, Cart, CartItem, Wishlist, Order, OrderItem


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    collection = CollectionSerializer(read_only=True)  # nested serializer
    collection_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'description', 'image', 'unit_price',
            'inventory', 'last_update', 'slug', 'collection', 'collection_id'
        ]


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity']


class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(source='cart_id', many=True, read_only=True)
    total_items = serializers.SerializerMethodField()
    total_value = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'session_id', 'created_at', 'cart_items', 'total_items', 'total_value']

    def get_total_items(self, obj):
        return sum(item.quantity for item in obj.cart_id.all())

    def get_total_value(self, obj):
        return sum(item.quantity * item.product.unit_price for item in obj.cart_id.all())


class WishlistSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    product_ids = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), many=True, write_only=True
    )

    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'products', 'product_ids', 'created_at']

    def create(self, validated_data):
        product_ids = validated_data.pop('product_ids', [])
        wishlist = Wishlist.objects.create(**validated_data)
        wishlist.products.set(product_ids)
        return wishlist


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_id', 'quantity', 'unit_price']


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    user_id = serializers.UUIDField(write_only=True)
    cart_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'user_id', 'cart', 'cart_id', 'total_amount', 'created_at', 'updated_at', 'order_items']
