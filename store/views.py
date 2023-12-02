from django.shortcuts import get_object_or_404
from django.db.models import Count
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from .models import Product,Collection,OrderItem
from .serializers import ProductSerializer,CollectionSerializer

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_serializer_context(self):
        return {"request":self.request}

    def destroy(self,request,*args,**kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count()>0:
             return Response({'error':'Product can not be deleted it is associated with orders'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(requst,*args, **kwargs)


class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(product_count= Count('products')).all()
    serializer_class = CollectionSerializer

    def destroy(self,request,*args, **kwargs):
        collection = get_object_or_404(Collection,pk=kwargs['pk'])
        if collection.products.count() > 0:
            return Response({'error':'Collection can not be deleted it is associated with products'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        