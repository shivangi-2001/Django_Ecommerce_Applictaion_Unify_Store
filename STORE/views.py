from typing import Any
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.db.models.query import QuerySet
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, get_list_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView, TemplateView, DeleteView, UpdateView
from rest_framework.viewsets import ModelViewSet
import datetime

from .filters import ProductFilter
from .forms import ProductForm, CartItemForm, UpdateQuantityForm
from .models import Product, Collection, Cart, CartItem
from .serializer import ProductSerializer, CollectionSerializer


user = get_user_model()

class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class WelcomePage(TemplateView):
    template_name = 'index.html'
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context =  super().get_context_data(**kwargs)
        context['new_products']=get_list_or_404(Product.objects.select_related('collection').order_by('?'), unit_price__lt=8, inventory__gt=20, last_update__gt=datetime.date(2023, 11, 20))[:8]
        return context

  
class CategoriesView(ListView):
    model = Collection
    template_name = 'Collection/categories.html'
    
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        # Recommended Products
        context['recommend_products'] = get_list_or_404(Product.objects.order_by('?'), unit_price__lt=8)[:8]
        context['new_products'] = get_list_or_404(Product.objects.order_by('?'), inventory__gt=50, last_update__gt=datetime.date(2023, 11, 20))[:8]
        return context

class ProductGallery(ListView):
    model = Product
    template_name = 'Product/product_gallery.html'
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
    template_name = 'Product/product_details.html'

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
    cart, created = Cart.objects.get_or_create(user_id=request.user.id)
    cart_item, cart_item_created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not cart_item_created:
        cart_item.quantity += 1
        cart_item.save()
    return HttpResponseRedirect('/products')


class CartView(ListView):
    model = Cart
    template_name = 'Cart/cart_view.html'
    paginate_by = 6

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        current_cart = self.get_queryset().get()
        context['cartItems'] = get_list_or_404(CartItem, cart_id=current_cart.id)
        product_info_list = [((cart_item.id),(cart_item.product_id), cart_item.quantity) for cart_item in context['cartItems']]
        cart_products = []
        for id, product, quantity in product_info_list:
            res = {
                "id": id,
                "product_id": get_object_or_404(Product, id=product),
                "quantity": quantity,
                "total_count": float(get_object_or_404(Product, id=product).unit_price * quantity)
            }
            cart_products.append(res)
        context['cart_products'] = cart_products
        return context


class UpdateCartItem(UpdateView):
    model = CartItem
    template_name = 'Cart/update.html'
    form_class = UpdateQuantityForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        print(context)
        return context
    def get_success_url(self):
        user_id = self.kwargs['user_id']
        return reverse_lazy('user_cart', kwargs={'user_id': user_id})

class DeleteCartItem(DeleteView):
    model = CartItem
    template_name = 'Cart/cart_view.html'
    def get_success_url(self):
        user_id = self.kwargs['user_id']
        return reverse_lazy('user_cart', kwargs={'user_id':user_id})