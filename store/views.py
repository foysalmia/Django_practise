from django.shortcuts import get_object_or_404
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend 
from rest_framework.response import Response
from rest_framework import status
from rest_framework.filters import SearchFilter,OrderingFilter
from rest_framework.mixins import CreateModelMixin,RetrieveModelMixin,DestroyModelMixin
from rest_framework.viewsets import ModelViewSet,GenericViewSet
from .models import Product,Collection,OrderItem,Review,Cart,CartIteam
from .serializers import ProductSerializer,CollectionSerializer,ReviewSerializer,CartSerializer,CartItemSerializer
from .filter import ProductFilter
from .pagination import DefalutPagination

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend,SearchFilter,OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['title','description']
    ordering_fields = ['unit_price','last_update']
    pagination_class = DefalutPagination

    def get_serializer_context(self):
        return {"request":self.request}

    def destroy(self,request,*args,**kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count()>0:
             return Response({'error':'Product can not be deleted it is associated with orders'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request,*args, **kwargs)


class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(product_count= Count('products')).all()
    serializer_class = CollectionSerializer

    def destroy(self,request,*args, **kwargs):
        collection = get_object_or_404(Collection,pk=kwargs['pk'])
        if collection.products.count() > 0:
            return Response({'error':'Collection can not be deleted it is associated with products'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ReviewViewSet(ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(product_id = self.kwargs['product_pk'])

    def get_serializer_context(self):
        return {'product_id':self.kwargs['product_pk']}
        

class CartViewSet(CreateModelMixin,RetrieveModelMixin,DestroyModelMixin,GenericViewSet):
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer

class CartItemViewSet(ModelViewSet):
    serializer_class = CartItemSerializer
    
    def get_queryset(self):
        return CartIteam.objects.filter(cart_id = self.kwargs['cart_pk']).select_related('product')
    
