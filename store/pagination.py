from rest_framework.pagination import PageNumberPagination

class DefalutPagination(PageNumberPagination):
    page_size = 10