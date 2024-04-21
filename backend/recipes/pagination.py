from rest_framework.pagination import PageNumberPagination


class CurrentPagination(PageNumberPagination):
    page_size_query_param = 'limit'
