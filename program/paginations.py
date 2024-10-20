from rest_framework import pagination


class MessageListPagination(pagination.PageNumberPagination):
    page_size = 200
    page_size_query_param = "page_size"
    max_page_size = 300
