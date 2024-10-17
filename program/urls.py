from django.urls import path
from .views import (
    ProgramListView,
    ProgramDetailView,
    NoticeDetailView,
    AssignmentDetailView,
    SubmitCreateView,
    SubmitUpdateView,
    OtherSubmitListView,
    OtherSubmitDetailView,
    CompanyProgramListView,
    CompanyProgramStartView,
    CompanyProgramDetaillView,
    CompanyProgramWarningView,
    CompanyProgramWarningCreateView,
    CompanyProgramNoticeDetailView,
    CompanyProgramNoticeCreateView,
    CompanyProgramAssignmentDetailView,
    CompanyProgramAssignmentCreateView,
    CompanyProgramAssignmentSubmitListView,
    CompanyProgramAssignmentSubmitDetailView,
    CompanyProgramAssignmentDurationExtendView,
    CompanyProgramSubmitRevisionView,
    CompanyProgramSubmitApprovalView,
)

urlpatterns = [
    ##학생
    # 나의활동: 진행중,완료활동 리스트
    path(
        "student/program/",
        ProgramListView.as_view(),
        name="student-program-list",
    ),
    # v 나의활동/활동1: 공지,과제 리스트
    path(
        "student/program/<int:pk>/",
        ProgramDetailView.as_view(),
        name="student-program-detail",
    ),
    # v 나의활동/활동1/공지: 공지
    path(
        "student/program/<int:program_id>/notice/<int:pk>/",
        NoticeDetailView.as_view(),
        name="student-program-notice",
    ),
    # v 나의활동/활동1/과제: 과제
    path(
        "student/program/<int:program_id>/assignment/<int:pk>/",
        AssignmentDetailView.as_view(),
        name="student-program-assignment",
    ),
    # v 나의활동/활동1/과제/과제제출: 과제 제출 버튼
    path(
        "student/program/<int:program_id>/assignment/<int:assignment_id>/submit/",
        SubmitCreateView.as_view(),
        name="student-assignment-submit",
    ),
    # v 나의활동/활동1/과제/수정: 과제 수정
    path(
        "student/program/<int:program_id>/assignment/<int:assignment_id>/submit/update/",
        SubmitUpdateView.as_view(),
        name="student-assignment-submit-update",
    ),
    # v 과제/다른사람 제출물 : 해당 과제 다른 참여자 제출 리스트
    path(
        "student/program/<int:program_id>/assignment/<int:assignment_id>/others/",
        OtherSubmitListView.as_view(),
        name="student-submit-others",
    ),
    # v 과제/다른사람제출물/사람1 : 해당 과제 다른 참여자 제출물
    path(
        "student/program/<int:program_id>/assignment/<int:assignment_id>/others/<int:submit_id>/",
        OtherSubmitDetailView.as_view(),
        name="student-submit-others-detail",
    ),
    ###################################################################################################################
    ##기업
    # 활동관리: 진행중, 완료활동 리스트
    path(
        "company/program/",
        CompanyProgramListView.as_view(),
        name="company-program-list",
    ),
    # 활동관리/활동1/활동 시작: 대외활동 시작
    path(
        "company/program/<int:pk>/start/",
        CompanyProgramStartView.as_view(),
        name="company-program-start",
    ),
    # v 활동관리/활동1: 공지,과제 리스트
    path(
        "company/program/<int:activity_id>/",
        CompanyProgramDetaillView.as_view(),
        name="company-program-detail",
    ),
    # v 활동관리/활동1/참여자 경고 부여 : 참여자 경고 부여 화면창
    path(
        "company/program/<int:activity_id>/warning/",
        CompanyProgramWarningView.as_view(),
        name="company-program-warning",
    ),
    # v 활동관리/활동1/경고 부여하기: 참여자 한명 경고 부여하기
    path(
        "company/program/<int:activity_id>/warning/create/",
        CompanyProgramWarningCreateView.as_view(),
        name="company-program-applicant-warning-create",
    ),
    # v 활동관리/활동1/공지: 공지
    path(
        "company/program/<int:activity_id>/notice/<int:pk>/",
        CompanyProgramNoticeDetailView.as_view(),
        name="company-program-notice-detail",
    ),
    # v 활동관리/활동1/공지/공지 작성: 공지 작성
    path(
        "company/program/<int:activity_id>/notice/create/",
        CompanyProgramNoticeCreateView.as_view(),
        name="company-program-notice-create",
    ),
    # v 활동관리/활동1/과제: 과제
    path(
        "company/program/<int:activity_id>/assignment/<int:pk>/",
        CompanyProgramAssignmentDetailView.as_view(),
        name="company-program-assignment-detail",
    ),
    # v 활동관리/활동1/과제/과제 작성: 과제 작성
    path(
        "company/program/<int:activity_id>/assignment/create/",
        CompanyProgramAssignmentCreateView.as_view(),
        name="company-program-assignment-create",
    ),
    # v 등록된 과제/과제 제출자
    path(
        "company/program/assignment/<int:assignment_id>/submit/",
        CompanyProgramAssignmentSubmitListView.as_view(),
        name="company-assignment-submit-list",
    ),
    # v 등록된 과제/과제 제출자/제출 내용
    path(
        "company/program/assignment/<int:assignment_id>/submit/<int:pk>/",
        CompanyProgramAssignmentSubmitDetailView.as_view(),
        name="company-assignment-submit-detail",
    ),
    # v 활동관리/활동1/과제/마감기한 연장
    path(
        "company/program/assignment/<int:pk>/extend/",
        CompanyProgramAssignmentDurationExtendView.as_view(),
        name="company-program-assignment-duration-extend",
    ),
    # v 등록된 과제/과제 제출자/수정요구: 제출 수정요구(1,2차)
    path(
        "company/program/submit/<int:pk>/revise/",
        CompanyProgramSubmitRevisionView.as_view(),
        name="company-program-submit-revise",
    ),
    # v 등록된 과제/과제 제출자/최종 승인: 제출 최종승인
    path(
        "company/program/submit/<int:pk>/approve/",
        CompanyProgramSubmitApprovalView.as_view(),
        name="company-program-approve",
    ),
]
