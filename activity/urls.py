from django.urls import path
from .views import (
    BoardListView,
    BoardDetailView,
    BoardCreateView,
    BoardDurationExtendView,
    CompanyUserBoardListView,
    CompanyUserBoardDetailView,
    ScrapBoardListView,
    ScrapBoardDetailView,
    ScrapCreateView,
    ScrapDeleteView,
    FormFillView,
    FormCreateView,
    FormBoardListView,
    FormBoardDetailView,
    FormDetailView,
    CompanyActivityListView,
    CompanyActivityFormListView,
    CompanyActivityFormDetailView,
    CompanyActivityFormConfirmView,
    CompanyActivityFormRejectView,
    FormActivityAcceptView,
    FormActivityCancelView,
    CompanyStudentProfileListView,
    CompanyStudentProfileDetailView,
    CompanyStudentPortfolioDetailView,
    CompanyStudentSuggestionCreateView,
    SuggestionListView,
)

urlpatterns = [
    # v 홈/로그인 전 : 게시글 목록(전부)
    path(
        "board/",
        BoardListView.as_view(),
        name="board-list",
    ),
    # v 대외활동 게시글/로그인 전 : 게시글 하나(전부)
    path(
        "board/<int:pk>/",
        BoardDetailView.as_view(),
        name="board-detail",
    ),
    # v 대외활동 게시글 추가하기 : 게시글 생성
    path(
        "company/board/create/",
        BoardCreateView.as_view(),
        name="board-create",
    ),
    # v 대외활동 게시글/마감기한 연장(7일) : 게시글 마감기한연장
    path(
        # board의 pk
        "company/board/<int:pk>/extend/",
        BoardDurationExtendView.as_view(),
        name="board_duration-extend",
    ),
    # v 활동등록 : 기업유저가 등록한 게시글 리스트
    path(
        "company/board/",
        CompanyUserBoardListView.as_view(),
        name="company-board-list",
    ),
    # v 대외활동 게시글 : 기업유저가 등록한 게시글 하나
    path(
        "company/board/<int:pk>/",
        CompanyUserBoardDetailView.as_view(),
        name="company-board-detail",
    ),
    # v 지원관리 : 기업유저가 등록한 '대외활동' 목록
    path(
        "company/activity/",
        CompanyActivityListView.as_view(),
        name="company-activity-list",
    ),
    # 지원관리/대외활동1 : 등록한 대외활동 목록 중 특정 대외활동에 지원한 지원자 목록
    path(
        "company/activity/<int:activity_id>/form/",
        CompanyActivityFormListView.as_view(),
        name="company-activity-form-list",
    ),
    # 지원관리/대외활동1/지원자1 : 지원자 한명의 지원서
    path(
        "company/activity/<int:activity_id>/form/<int:pk>/",
        CompanyActivityFormDetailView.as_view(),
        name="company-activity-form-detail",
    ),
    # 지원관리/대외활동1/지원자1/합격 : 지원자 한명의 지원서 합격처리
    path(
        "company/form/<int:pk>/confirm/",
        CompanyActivityFormConfirmView.as_view(),
        name="company-activity-form-confirm",
    ),
    # 지원관리/대외활동1/지원자1/불합격 : 지원자 한명의 지원서 불합격처리
    path(
        "company/form/<int:pk>/reject/",
        CompanyActivityFormRejectView.as_view(),
        name="company-activity-form-reject",
    ),
    # v 지원관리/스크랩 : 스크랩 한 게시글 리스트
    path(
        "student/scrap/board/",
        ScrapBoardListView.as_view(),
        name="scrap-board-list",
    ),
    # v 지원관리/스크랩/게시글 : 스크랩 한 게시글 하나
    path(
        "student/scrap/board/<int:pk>/",
        ScrapBoardDetailView.as_view(),
        name="scrap-board-detail",
    ),
    # v 대외활동 게시글/로그인 경우/스크랩 : 스크랩하기
    path(
        "student/scrap/create/",
        ScrapCreateView.as_view(),
        name="scrap-create",
    ),
    # v 대외활동 게시글/로그인 경우/스크랩 : 스크랩취소
    path(
        "student/scrap/delete/<int:board_pk>/",
        ScrapDeleteView.as_view(),
        name="scrap-delete",
    ),
    # v 지원 페이지/포트폴리오 있음 : 지원서 작성 화면
    path(
        "student/form/fill/",
        FormFillView.as_view(),
        name="form-fill",
    ),
    # v 지원 페이지/포트폴리오 있음/지원서 제출하기 : 지원서 제출
    path(
        "student/form/create/",
        FormCreateView.as_view(),
        name="form-create",
    ),
    # v 지원관리/지원완료 : 지원서 제출한 게시물(대외활동) 리스트
    path(
        "student/form/board/",
        FormBoardListView.as_view(),
        name="form-board-list",
    ),
    # v 대외활동 게시글/지원완료 : 지원서 제출한 게시물(대외활동) 하나
    path(
        # form의 pk
        "student/form/board/<int:pk>/",
        FormBoardDetailView.as_view(),
        name="form-board-detail",
    ),
    # v 제출완료 지원서 : 제출완료한 지원서
    path(
        # form의 pk, 위의 pk와 같음
        "student/form/<int:pk>/",
        FormDetailView.as_view(),
        name="form-detail",
    ),
    # 대외활동 게시글/확정대기/활동 최종 확정 : 합격한 대외활동 최종 활동 확정
    path(
        "student/form/<int:pk>/accept/",
        FormActivityAcceptView.as_view(),
        name="form-activity-accept",
    ),
    # 대외활동 게시글/확정대기/활동 취소 : 합격한 대외활동 활동 취소
    path(
        "student/form/<int:pk>/cancel/",
        FormActivityCancelView.as_view(),
        name="form-activity-cancel",
    ),
    # 학생 프로필 검색
    path(
        "company/profile/",
        CompanyStudentProfileListView.as_view(),
        name="company-student-profile-list",
    ),
    # 학생 프로필 검색/프로필1
    path(
        "company/profile/<int:profile_id>/",
        CompanyStudentProfileDetailView.as_view(),
        name="company-student-profile-detail",
    ),
    # 학생 프로필 검색/프로필1/포트폴리오1
    path(
        "company/profile/<int:profile_id>/portfolio/<int:pk>/",
        CompanyStudentPortfolioDetailView.as_view(),
        name="company-student-portfolio-detail",
    ),
    # 학생 프로필 검색/프로필1/지원제안 보내기
    path(
        "company/profile/<int:profile_id>/suggest/",
        CompanyStudentSuggestionCreateView.as_view(),
        name="company-profile-suggest",
    ),
    # 포트폴리오/지원제안 : 들어온 지원제안
    path(
        "student/suggestion/",
        SuggestionListView.as_view(),
        name="student-suggestion",
    ),
]
