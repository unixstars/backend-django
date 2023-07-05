from rest_framework import generics, permissions, pagination
from .models import Board
from .serializers import BoardSerializer


class BoardListPagination(pagination.PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class BoardListView(generics.ListAPIView):
    queryset = Board.objects.order_by("-views", "-created_at").all()
    serializer_class = BoardSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = BoardListPagination
