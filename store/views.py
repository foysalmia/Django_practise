from django.shortcuts import get_object_or_404
from django.db.models import Count
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend 
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated,AllowAny,IsAdminUser
from rest_framework.filters import SearchFilter,OrderingFilter
from rest_framework.mixins import CreateModelMixin,RetrieveModelMixin,DestroyModelMixin,UpdateModelMixin
from rest_framework.viewsets import ModelViewSet,GenericViewSet
from .models import Product,Collection,OrderItem,Review,Cart,CartIteam
from .serializers import *
from .filter import ProductFilter
from .pagination import DefalutPagination
from .permissions import IsAdminOrReadOnly

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend,SearchFilter,OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['title','description']
    ordering_fields = ['unit_price','last_update']
    pagination_class = DefalutPagination
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_context(self):
        return {"request":self.request}

    def destroy(self,request,*args,**kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count()>0:
             return Response({'error':'Product can not be deleted it is associated with orders'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request,*args, **kwargs)


class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(product_count= Count('products')).all()
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]

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
    http_method_names = ['get','post','patch','delete']
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdatedCartItemSerializer
        return CartItemSerializer
    
    def get_serializer_context(self):
        return {'cart_id':self.kwargs['cart_pk']}

    def get_queryset(self):
        return CartIteam.objects.filter(cart_id = self.kwargs['cart_pk']).select_related('product')
    
class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminUser]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(detail=False,methods=['GET','PUT'],permission_classes = [IsAuthenticated])
    def me(self,request):
        (customer,created) = Customer.objects.get_or_create(user_id = request.user.id)
        if request.method == 'GET':
            serializer= CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method =='PUT':
            serializer = CustomerSerializer(customer,data = request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class OrderViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    http_method_names = ['get','post','patch','delete','head','options']

    def get_permissions(self):
        if self.request.method in ['PATCH','DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(data=request.data,context={'user_id': self.request.user.id})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        elif self.request.method == 'PATCH':
            return UpdateOrderSerializer
        return OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        (customer_id,created) = Customer.objects.only('id').get_or_create(user_id = user.id)
        return Order.objects.filter(customer_id = customer_id)
    