from django_filters import FilterSet, NumberFilter, CharFilter, OrderingFilter
from STORE.models import Product

class ProductFilter(FilterSet):
    min_price = NumberFilter(field_name='unit_price', lookup_expr='gte', label='Min Price')
    max_price = NumberFilter(field_name='unit_price', lookup_expr='lte', label='Max Price')
    product_title = CharFilter(field_name='title', lookup_expr='icontains', label='Product Title')
    
    ordering = OrderingFilter(
        fields=(
            ('inventory', 'inventory'),
            ('unit_price', 'unit_price'),
        ),
        field_labels={
            'inventory': 'Inventory',
            'unit_price': 'Price',
        },
        label='Sort By'
    )

    class Meta:
        model = Product
        fields = ['min_price', 'max_price', 'product_title', 'inventory', 'unit_price', 'collection_id']
