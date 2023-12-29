from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static

from .views import CollectionViewSet, CategoriesView, ProductViewSet, ProductGallery, serach_product_collection, \
    ProductDetails, \
    home_page, add_to_cart, CartView

router = DefaultRouter()
router.register(r'product', ProductViewSet, basename='product')
router.register(r'collection', CollectionViewSet, basename='collection')

urlpatterns = [
    path('', home_page, name='home_page'),
    path('search/', serach_product_collection),
    path('categories/', CategoriesView.as_view(), name='categories'),
    path('products/', ProductGallery.as_view(), name="products"),
    path('products/<str:pk>/', ProductDetails.as_view()),
    path('products/<str:pk>/add_to_cart', add_to_cart, name='add_to_cart'),
    path('cart/<str:pk>/', CartView.as_view(), name='your_cart')
] + router.urls

if settings.DEBUG:
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)