from django.urls import path
from .views import BoardListView

urlpatterns = [
    path("board/list/", BoardListView.as_view(), name="board-list"),
]
