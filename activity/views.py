from rest_framework import generics, permissions, pagination
from .models import Board
from .serializers import BoardSerializer


class BoardListPagination(pagination.PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class BoardListView(generics.ListAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = BoardListPagination

    # 게시판 필터링을 위해 기업 id를 parameter형태로 제공(optional), 여러 파라미터를 쉼표에 따라 분리.
    def get_queryset(self):
        queryset = Board.objects.all()
        company_ids = self.request.query_params.get("company_id", None)
        if company_ids is not None:
            company_ids = [int(id) for id in company_ids.split(",")]
            queryset = queryset.filter(company_user_id__in=company_ids)
        return queryset
