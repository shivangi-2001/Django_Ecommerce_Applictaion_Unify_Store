from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static

from .views import (CollectionViewSet, CategoriesView, ProductViewSet, ProductGallery, serach_product_collection, \
    ProductDetails, WelcomePage, add_to_cart, CartView, DeleteCartItem, ViewWishlist, Increase_quantity_cartItems,
                    Decrease_qunatity_cartItems, CreateOrder)

router = DefaultRouter()
router.register(r'product', ProductViewSet, basename='product')
router.register(r'collection', CollectionViewSet, basename='collection')

urlpatterns = [
    path('', WelcomePage.as_view(), name='index'),
    path('search/', serach_product_collection),
    path('categories/', CategoriesView.as_view(), name='categories'),
    path('products/', ProductGallery.as_view(), name="products"),
    path('products/<str:pk>/', ProductDetails.as_view()),
    path('products/<str:pk>/add_to_cart', add_to_cart, name='add_to_cart'),
    path('cart/<str:user_id>/', CartView.as_view(), name='user_cart'),
    path('cartItem/<str:cart_items_id>/', Increase_quantity_cartItems, name="increase_quantity"),
    path('cartItem/<str:cart_items_id>/-', Decrease_qunatity_cartItems, name="decrease_quantity"),
    path('cart/<str:user_id>/delete/<str:pk>', DeleteCartItem.as_view(), name='delete_cart_item'),
    path('wishlist', ViewWishlist.as_view(), name="user_wishlist"),
    path('order/', CreateOrder, name="order")
] + router.urls

if settings.DEBUG:
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)