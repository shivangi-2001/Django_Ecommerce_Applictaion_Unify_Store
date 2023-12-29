from typing import Any
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.db.models.query import QuerySet
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, get_list_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView
from rest_framework.viewsets import ModelViewSet
import datetime

from .filters import ProductFilter
from .forms import ProductForm, CartItemForm
from .models import Product, Collection, Cart, CartItem
from .serializer import ProductSerializer, CollectionSerializer


user = get_user_model()

class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

def home_page(request):
    return render(request, 'home.html')

  
class CategoriesView(ListView):
    model = Collection
    template_name = 'categories.jinja'
    
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        # Recommended Products
        context['recommend_products'] = get_list_or_404(Product.objects.order_by('?'), unit_price__lt=8)[:8]
        context['new_products'] = get_list_or_404(Product.objects.order_by('?'), inventory__gt=50, last_update__gt=datetime.date(2023, 11, 20))[:8]
        return context

class ProductGallery(ListView):
    model = Product
    template_name = 'product_gallery.html'
    form_class = ProductForm
    paginate_by = 20
    filterset_class = ProductFilter
    filterset_fields = ['collection_id', 'unit_price']

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset
        context['count'] = self.get_queryset().count()
        return context
    
def serach_product_collection(request):
        search = request.GET.get('search')
        if search:
            products = Product.objects.filter(title__icontains=search).order_by('title')[:10]
            payload = [product.title for product in products]
            return JsonResponse({
                'status': 'successful',
                'data': payload
            })
        else:
            return JsonResponse("Does not have any Template for these route")

class ProductDetails(DetailView):
    model = Product
    template_name = 'product_details.html'

    def get_object(self, queryset=None):
        product_id = self.kwargs['pk']
        queryset = Product.objects.select_related('collection')
        return get_object_or_404(queryset, id=product_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['collection_title'] = self.object.collection.title
        return context

def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart, created = Cart.objects.get_or_create()
    cart_item, cart_item_created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not cart_item_created:
        cart_item.quantity += 1
        cart_item.save()
    return HttpResponseRedirect('/products')


class CartView(DetailView):
    model = Cart
    template_name = 'cart_view.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context =  super().get_context_data(**kwargs)
        current_cart = self.get_queryset()
        context['CartItem'] = get_list_or_404(CartItem, cart_id=current_cart[0])
        print(context)
        return context