from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
router.register("products",views.ProductViewSet,basename='products')
router.register("collections",views.CollectionViewSet)
router.register('carts',views.CartViewSet)

product_router = routers.NestedDefaultRouter(router,'products',lookup = 'product')
product_router.register('reviews',views.ReviewViewSet,basename='product-reviews')

cart_item_router = routers.NestedDefaultRouter(router,'carts',lookup='cart' )
cart_item_router.register('items',views.CartItemViewSet,basename='cart_items')

urlpatterns = router.urls + product_router.urls+cart_item_router.urls