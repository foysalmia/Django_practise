import django_filters
from .models import Product

class ProductFilter(django_filters.FilterSet):
    collection_id = django_filters.NumberFilter()
    Unit_price__gt = django_filters.NumberFilter(field_name='unit_price', lookup_expr='gt')
    unit_price__lt = django_filters.NumberFilter(field_name='unit_price', lookup_expr='lt')
    class Meta:
        product = Product
        fields  = ['collection_id','unit_price']
        