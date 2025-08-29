from rest_framework import viewsets, permissions
from .models import Product, Collection, Cart, CartItem, Wishlist, Order, OrderItem
from .serializer import (
    ProductSerializer, CollectionSerializer, CartSerializer, CartItemSerializer,
    WishlistSerializer, OrderSerializer, OrderItemSerializer
)


class CollectionViewSet(viewsets.ModelViewSet):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
    permission_classes = [permissions.AllowAny]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().select_related("collection")
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all().prefetch_related("cart_id")
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]


class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all().select_related("cart", "product")
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]


class WishlistViewSet(viewsets.ModelViewSet):
    queryset = Wishlist.objects.all().prefetch_related("products")
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().prefetch_related("order_items")
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all().select_related("order", "product")
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]
