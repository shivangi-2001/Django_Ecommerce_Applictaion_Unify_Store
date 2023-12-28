from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static

from .views import CollectionViewSet, ProductViewSet, ProductGallery, serach_product_collection, ProductDetails, \
    home_page

router = DefaultRouter()
router.register(r'product', ProductViewSet, basename='product')
router.register(r'collection', CollectionViewSet, basename='collection')

urlpatterns = [
    path('', home_page, name='home_page'),
    path('search/', serach_product_collection),
    path('products/', ProductGallery.as_view(), name="prod"),
    path('products/<str:pk>/', ProductDetails.as_view())
] + router.urls

if settings.DEBUG:
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)