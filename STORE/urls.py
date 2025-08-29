from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static
from .api_views import ProductViewSet, CollectionViewSet, CartViewSet, CartItemViewSet, WishlistViewSet, OrderViewSet, OrderItemViewSet
from .views import (CategoriesView, ProductGallery, serach_product_collection, ProductDetails, WelcomePage, 
                    add_to_cart, CartView, increase_quantity, decrease_quantity, delete_cart_item, ViewWishlist, CreateOrder)

router = DefaultRouter()
router.register("collections", CollectionViewSet)
router.register("products", ProductViewSet)
router.register("carts", CartViewSet)
router.register("cart-items", CartItemViewSet)
router.register("wishlists", WishlistViewSet)
router.register("orders", OrderViewSet)
router.register("order-items", OrderItemViewSet)

urlpatterns = [
    path('', WelcomePage.as_view(), name='index'),
    path('search/', serach_product_collection),
    
    path('categories/', CategoriesView.as_view(), name='categories'),
    path('products/', ProductGallery.as_view(), name="products"),
    path('products/<str:pk>/', ProductDetails.as_view(), name="product_details"),

    path('products/<str:pk>/add_to_cart', add_to_cart, name='add_to_cart'),
    path("cart/", CartView.as_view(), name="user_cart"),
    path("session-cart/", CartView.as_view(), name="session_cart"),

    path('cartItem/<str:cart_items_id>/', increase_quantity, name="increase_quantity"),
    path('cartItem/<str:cart_items_id>/-', decrease_quantity, name="decrease_quantity"),
    path('cart/<str:user_id>/delete/<str:pk>', delete_cart_item, name='delete_cart_item'),
    
    path('wishlist', ViewWishlist.as_view(), name="user_wishlist"),
    
    path('order/', CreateOrder.as_view(), name="place_order")
] + router.urls

if settings.DEBUG:
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)