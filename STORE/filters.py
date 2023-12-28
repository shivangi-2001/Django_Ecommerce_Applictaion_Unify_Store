from django_filters import FilterSet, NumberFilter, CharFilter

from STORE.models import Product


class ProductFilter(FilterSet):
    min_price = NumberFilter(field_name='unit_price', lookup_expr='gte', label='Min Price')
    max_price = NumberFilter(field_name='unit_price', lookup_expr='lte', label='Max Price')
    product_title = CharFilter(field_name='title', lookup_expr='icontains')
    class Meta:
        model = Product
        fields = [ 'collection_id', 'min_price', 'max_price', 'product_title']