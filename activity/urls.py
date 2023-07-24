from django.urls import path
from .views import (
    BoardListView,
    BoardDetailView,
    BoardCreateView,
    BoardDurationExtendView,
)

urlpatterns = [
    path("board/", BoardListView.as_view(), name="board-list"),
    path("board/<int:pk>/", BoardDetailView.as_view(), name="board-detail"),
    path("board/create/", BoardCreateView.as_view(), name="board-create"),
    path(
        "board/<int:pk>/extend/",
        BoardDurationExtendView.as_view(),
        name="board_duration-extend",
    ),
]
