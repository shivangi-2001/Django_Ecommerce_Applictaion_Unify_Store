from typing import Any
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, get_list_or_404, redirect
from django.views import View
from django.views.generic import ListView, DetailView, TemplateView, DeleteView, CreateView

import datetime

from .filters import ProductFilter
from .forms import ProductForm
from .models import Product, Collection, Cart, CartItem, Wishlist, Order, OrderItem
from .serializer import ProductSerializer, CollectionSerializer


USER = get_user_model()

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
        context['collections'] = Collection.objects.all()

        context['active_collection_id'] = self.request.GET.get('collection_id')
        if self.request.user.is_authenticated:
            wishlist = Wishlist.objects.get_or_create(user=self.request.user)[0]
            context['wishlist_products'] = wishlist.products.values_list('id', flat=True)
            # print(context['wishlist_products'])
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
        product = context['product']

        min_price = max(product.unit_price - 20, 0)
        max_price = product.unit_price + 20

        context["similar_collection"] = Product.objects.filter(
            collection_id=product.collection.id,
            inventory__gt=0,
            unit_price__range=(min_price, max_price)
        ).exclude(id=product.id)[:4]  # exclude same product + limit results

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

# ---------------- ADD TO CART ----------------
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    quantity = int(request.POST.get("quantity", 1)) if request.POST.get("quantity") else 1

    # Find or create correct cart
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        cart, _ = Cart.objects.get_or_create(session_id=request.session.session_key)

    # Add or update item
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if created:
        cart_item.quantity = quantity
    else:
        cart_item.quantity += quantity
    cart_item.save()

    return redirect(request.META.get("HTTP_REFERER", "/"))


# ---------------- CART VIEW ----------------
class CartView(TemplateView):
    template_name = 'Cart/cart_view.html'

    def get_cart(self):
        if self.request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=self.request.user)
        else:
            if not self.request.session.session_key:
                self.request.session.create()
            cart, _ = Cart.objects.get_or_create(session_id=self.request.session.session_key)
        return cart

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = self.get_cart()
        cart_items = CartItem.objects.filter(cart=cart).select_related("product")

        cart_products = [
            {
                "id": item.id,
                "product": item.product,
                "quantity": item.quantity,
                "total_count": float(item.product.unit_price * item.quantity),
            }
            for item in cart_items
        ]

        context["cart_products"] = cart_products
        context["total_value"] = sum(item["total_count"] for item in cart_products)
        return context


# ---------------- QUANTITY UPDATE ----------------
def increase_quantity(request, cart_items_id):
    cart = _get_current_cart(request)
    cart_item = get_object_or_404(CartItem, id=cart_items_id, cart=cart)
    cart_item.quantity += 1
    cart_item.save()
    return redirect(request.META.get("HTTP_REFERER", "/"))

def decrease_quantity(request, cart_items_id):
    cart = _get_current_cart(request)
    cart_item = get_object_or_404(CartItem, id=cart_items_id, cart=cart)
    cart_item.quantity -= 1
    if cart_item.quantity <= 0:
        cart_item.delete()
    else:
        cart_item.save()
    return redirect(request.META.get("HTTP_REFERER", "/"))


# ---------------- DELETE ITEM ----------------
def delete_cart_item(request, cart_item_id):
    cart = _get_current_cart(request)
    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart=cart)
    cart_item.delete()
    return redirect("user_cart")


# ---------------- HELPER ----------------
def _get_current_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        cart, _ = Cart.objects.get_or_create(session_id=request.session.session_key)
    return cart

class ViewWishlist(View):
    def get(self, request):
        try:
            wish_id = Wishlist.objects.get(user_id=request.user.id)
            wish_product = wish_id.products.all()
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
    

class CreateOrder(View):
    def get(self, request):
        if not request.user.is_authenticated:
            messages.info(request, "You need to login to checkout")
        current_user = get_object_or_404(USER, email=request.user)

        current_user = get_object_or_404(USER, email=request.user)
        cart = _get_current_cart(request)
        cart_items = CartItem.objects.filter(cart=cart).select_related("product")

        if not cart_items.exists():
            messages.info(request, "Your cart is empty. Please add items to your cart before placing an order.")
            return redirect('products')

        product_cost = sum(item.product.unit_price * item.quantity for item in cart_items)

        total_price = product_cost
        shipping_cost=0
        if(total_price<50):
            shipping_cost=9
            total_price+=shipping_cost


        print(total_price, shipping_cost, )
        
        return render(request, template_name="Order/checkout_form.html", context={"user": current_user,"product_cost": product_cost, "total_price": total_price, "shipping_cost": shipping_cost})

    def post(self, request):
        if not request.user.is_authenticated:
            messages.info(request, "You need to login to checkout")
            return redirect('index')
        
        current_user = get_object_or_404(USER, email=request.user)
        cart = _get_current_cart(request)
        cart_items = CartItem.objects.filter(cart=cart).select_related("product")

        if not cart_items.exists():
            messages.info(request, "Your cart is empty. Please add items to your cart before placing an order.")
            return redirect('products')

        total_price = sum(item.product.unit_price * item.quantity for item in cart_items)

        # Create Order
        order = Order.objects.create(user=current_user, total_price=total_price, cart=cart)

        # Create OrderItems
        order_items = [
            OrderItem(
                order=order,
                product=item.product,
                quantity=item.quantity,
                unit_price=item.product.unit_price
            )
            for item in cart_items
        ]
        OrderItem.objects.bulk_create(order_items)

        # Clear Cart
        cart_items.delete()

        messages.success(request, "Your order has been placed successfully!")
        return redirect('index')

  
