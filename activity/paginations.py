from rest_framework import pagination


class BoardListPagination(pagination.PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class ProfileListPagination(pagination.PageNumberPagination):
    page_size = 30
    page_size_query_param = "page_size"
    max_page_size = 120


class MessageListPagination(pagination.PageNumberPagination):
    page_size = 200
    page_size_query_param = "page_size"
    max_page_size = 300
