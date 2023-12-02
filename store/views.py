from django.shortcuts import get_object_or_404
from django.db.models import Count
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from .models import Product,Collection,OrderItem,Review
from .serializers import ProductSerializer,CollectionSerializer,ReviewSerializer

class ProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.all()
        collection_id = self.request.query_params.get('collection_id')
        if collection_id is not None:
            queryset = queryset.filter(collection_id=collection_id)
        return queryset

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
        