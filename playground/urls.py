from django.urls import path
from . import views

urlpatterns = [
    path('say-hello',views.say_hello)
]
