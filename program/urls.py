from django.urls import path
from .views import (
    ProgramListView,
    ProgramDetailView,
    ProgramWarningView,
    NoticeDetailView,
    NoticeCommentListView,
    NoticeCommentCreateView,
    NoticeCheckUpdateView,
    AssignmentDetailView,
    AssignmentCommentListView,
    AssignmentCommentCreateView,
    SubmitCreateView,
    SubmitUpdateView,
)

urlpatterns = [
    ##학생
    # 나의활동: 진행중,완료활동 리스트
    path(
        "student/program/",
        ProgramListView.as_view(),
        name="student-program-list",
    ),
    # 나의활동/활동1: 공지,과제 리스트
    path(
        "student/program/<int:pk>/",
        ProgramDetailView.as_view(),
        name="student-program-detail",
    ),
    # 나의활동/활동1/경고: 받은 경고 리스트
    path(
        "student/program/<int:program_id>/warning/",
        ProgramWarningView.as_view(),
        name="student-program-warning",
    ),
    # 나의활동/활동1/공지: 공지
    path(
        "student/program/<int:program_id>/notice/<int:pk>/",
        NoticeDetailView.as_view(),
        name="student-program-notice",
    ),
    # (학생,기업) 공지 댓글 리스트
    path(
        "notice/<int:notice_id>/comment/",
        NoticeCommentListView.as_view(),
        name="notice-comment-list",
    ),
    # 나의활동/활동1/공지/댓글 작성: 공지 댓글 작성
    path(
        "student/notice/<int:notice_id>/comment/create/",
        NoticeCommentCreateView.as_view(),
        name="notice-comment-create",
    ),
    # 나의활동/활동1/공지/공지 확인: 공지 확인 버튼
    path(
        "student/notice/<int:pk>/check/",
        NoticeCheckUpdateView.as_view(),
        name="notice-check",
    ),
    # 나의활동/활동1/과제: 과제
    path(
        "student/program/<int:program_id>/assignment/<int:pk>/",
        AssignmentDetailView.as_view(),
        name="student-program-assignment",
    ),
    # (학생,기업) 과제 댓글 리스트
    path(
        "assignment/<int:assignment_id>/comment/",
        AssignmentCommentListView.as_view(),
        name="assignment-comment-list",
    ),
    # 나의활동/활동1/과제/댓글 작성: 과제 댓글 작성
    path(
        "student/assignment/<int:assignment_id>/comment/create/",
        AssignmentCommentCreateView.as_view(),
        name="assignment-comment-create",
    ),
    # 나의활동/활동1/과제/과제제출: 과제 제출 버튼
    path(
        "student/assignment/<int:assignment_id>/submit/",
        SubmitCreateView.as_view(),
        name="assignment-submit",
    ),
    # 나의활동/활동1/과제/수정: 과제 수정
    path(
        "student/assignment/<int:assignment_id>/submit/update/",
        SubmitUpdateView.as_view(),
        name="assignment-submit-update",
    ),
    ##기업
    # 활동관리: 진행중, 완료활동 리스트
    # 활동관리/활동1: 활동1 참여자 리스트
    # 활동관리/활동1/학생1: 공지,과제 리스트
    # 활동관리/활동1/학생1/경고: 부여한 경고 리스트
    # 활동관리/활동1/학생1/경고/경고하기: 경고 부여하기
    # 활동관리/활동1/학생1/공지: 공지
    # 활동관리/활동1/학생1/공지/공지 작성: 공지 작성
    # 활동관리/활동1/학생1/공지/댓글 작성: 공지 댓글 작성
    # 활동관리/활동1/학생1/과제: 과제
    # 활동관리/활동1/학생1/과제/과제 작성: 과제 작성
    # 활동관리/활동1/학생1/과제/댓글 작성: 과제 댓글 작성
    # 활동관리/활동1/학생1/과제: 과제 마감기한 연장
    # 활동관리/활동1/학생1/과제/수정요구: 과제 수정요구(1,2차)
    # 활동관리/활동1/학생1/과제/최종 승인: 과제 최종승인
]
