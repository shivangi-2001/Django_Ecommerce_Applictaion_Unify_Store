from typing import Any
from django.contrib.auth import get_user_model
from django.db import  transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, get_list_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, TemplateView, DeleteView
from rest_framework.viewsets import ModelViewSet
import datetime

from .filters import ProductFilter
from .forms import ProductForm
from .models import Product, Collection, Cart, CartItem, Wishlist, Order, OrderItem
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
        if self.request.user.is_authenticated:
            wishlist = Wishlist.objects.get_or_create(user=self.request.user)[0]
            context['wishlist_products'] = wishlist.products.values_list('id', flat=True)
        return context

  
class CategoriesView(ListView):
    model = Collection
    template_name = 'Collection/categories.html'

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        # Recommended Products
        context['recommend_products'] = get_list_or_404(Product, unit_price__lt=8)[:8]
        context['new_products'] = get_list_or_404(Product, inventory__gt=50, last_update__gt=datetime.date(2023, 11, 20))[:8]
        if self.request.user.is_authenticated:
            wishlist = Wishlist.objects.get_or_create(user=self.request.user)[0]
            context['wishlist_products'] = wishlist.products.values_list('id', flat=True)
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
        if self.request.user.is_authenticated:
            wishlist = Wishlist.objects.get_or_create(user=self.request.user)[0]
            context['wishlist_products'] = wishlist.products.values_list('id', flat=True)
            print(context['wishlist_products'])
        return context
    
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

def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart, created = Cart.objects.get_or_create(user_id=request.user.id)
    cart_item, cart_item_created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not cart_item_created:
        cart_item.quantity += 1
        cart_item.save()
    referring_url = request.META.get('HTTP_REFERER', '/')
    return redirect(referring_url)

class CartView(ListView):
    model = Cart
    template_name = 'Cart/cart_view.html'
    paginate_by = 6

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        cart_id, created = Cart.objects.get_or_create(user_id=self.request.user.id)
        cartItems = CartItem.objects.filter(cart_id=cart_id)
        product_list_id = [(cart_item.id, cart_item.product_id, cart_item.quantity) for cart_item in cartItems]
        cart_products = []
        for id, product, quantity in product_list_id:
            res = {
                "id": id,
                "product_id": get_object_or_404(Product, id=product),
                "quantity": quantity,
                "total_count": float(get_object_or_404(Product, id=product).unit_price * quantity)
            }
            cart_products.append(res)
        context['cart_products'] = cart_products
        total_value = 0
        for cart in cart_products:
            total_value+= cart['total_count']
        context['total_value'] = total_value
        return context

def Increase_quantity_cartItems(request, cart_items_id):
        current_product = get_object_or_404(CartItem, id=cart_items_id)
        current_product.quantity += 1
        current_product.save()
        referring_url = request.META.get('HTTP_REFERER', '/')
        return redirect(referring_url)

def Decrease_qunatity_cartItems(request, cart_items_id):
    current_product = get_object_or_404(CartItem, id=cart_items_id)
    current_product.quantity -= 1
    current_product.save()
    if current_product.quantity == 0:
        current_product.delete()
    referring_url = request.META.get('HTTP_REFERER', '/')
    return redirect(referring_url)

class DeleteCartItem(DeleteView):
    model = CartItem
    template_name = 'Cart/cart_view.html'
    def get_success_url(self):
        user_id = self.kwargs['user_id']
        return reverse_lazy('user_cart', kwargs={'user_id':user_id})


class ViewWishlist(View):
    def get(self, request):
        try:
            wish_id = Wishlist.objects.get(user_id=request.user.id)
            wish_product = wish_id.products.all()
            print(wish_product)
            # product = [Product.objects.get(id=product.id) for product in wish_product]
            # print(product)
            context = {
                'count': wish_product.count(),
                'products': wish_product
            }
            return render(request, template_name='wishlist/userWishlist.html', context=context)
        except:
            return render(request, template_name='wishlist/userWishlist.html')
    def post(self, request):
        current_user = request.user.id
        wish_product_id = request.POST.get('product_id')
        if 'remove_wish' in request.POST:
            product = get_object_or_404(Product, id=wish_product_id)
            wishlist = Wishlist.objects.get_or_create(user_id=current_user)[0]

            if wishlist.products.filter(id=product.id).exists():
                wishlist.products.remove(product)
        else:
            product = get_object_or_404(Product, id=wish_product_id)
            wishlist, created = Wishlist.objects.get_or_create(user_id=current_user)
            wishlist.products.add(product)
        referring_url = request.META.get('HTTP_REFERER', '/')
        return redirect(referring_url)

def CreateOrder(request):
        context = {}
        if request.method == 'POST':
            user_id = request.user.id
            cart = get_object_or_404(Cart, user_id=user_id)
            total_amount = request.POST.get('total_amount')

            with transaction.atomic():
                if float(total_amount) > 0:
                    order_created, created = Order.objects.get_or_create(user_id=user_id, cart=cart,
                                                                         total_amount=total_amount)

                    cart_items = CartItem.objects.filter(cart=cart)

                    # Calculate total price for each product in the cart
                    product_totals = []
                    for cart_item in cart_items:
                        product_total = cart_item.product.unit_price * cart_item.quantity
                        product_totals.append({'product': cart_item.product, 'total_price': product_total})
                        OrderItem.objects.get_or_create(
                            order=order_created,
                            product=cart_item.product,
                            quantity=cart_item.quantity,
                            unit_price=cart_item.product.unit_price
                        )

                    # Calculate the overall sum of item prices
                    overall_sum = sum(product_total['total_price'] for product_total in product_totals)
                    context['count'] = len(product_totals)
                    context['products'] = product_totals
                    context['overall_sum'] = overall_sum
                else:
                    help_text = "Add Product into your Cart"
                    context['help_text'] = help_text

            return render(request, template_name='Checkout/checkout_form.html', context=context)



