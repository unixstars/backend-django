from django.urls import path
from .views import (
    ProgramListView,
    ProgramDetailView,
    ProgramWarningView,
    ApplicantCommentListView,
    ApplicantCommentCreateView,
    NoticeDetailView,
    NoticeCommentListView,
    NoticeCommentCreateView,
    NoticeCheckUpdateView,
    AssignmentDetailView,
    AssignmentCommentListView,
    AssignmentCommentCreateView,
    SubmitCreateView,
    SubmitUpdateView,
    OtherSubmitListView,
    OtherSubmitDetailView,
    CompanyProgramListView,
    CompanyProgramStartView,
    CompanyProgramDetaillView,
    CompanyProgramWarningView,
    CompanyProgramWarningCreateView,
    CompanyApplicantCommentListView,
    CompanyApplicantCommentCreateView,
    CompanyProgramNoticeDetailView,
    CompanyProgramNoticeCreateView,
    CompanyProgramNoticeCommentCreateView,
    CompanyProgramAssignmentDetailView,
    CompanyProgramAssignmentCreateView,
    CompanyProgramAssignmentCommentCreateView,
    CompanyProgramAssignmentSubmitListView,
    CompanyProgramAssignmentSubmitDetailView,
    CompanyProgramAssignmentDurationExtendView,
    CompanyProgramAssignmentRevisionView,
    CompanyProgramAssignmentApprovalView,
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
    # v 나의활동/활동1/소통댓글창 : 대외활동 기업 및 참여자 댓글 반환
    path(
        "student/program/<int:program_id>/comment/",
        ApplicantCommentListView.as_view(),
        name="student-program-comment",
    ),
    # v 나의활동/활동1/소통댓글창/등록 : 학생 댓글 등록
    path(
        "student/program/<int:program_id>/comment/create/",
        ApplicantCommentCreateView.as_view(),
        name="student-program-comment-create",
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
    # v 활동관리/활동1/소통 댓글창: 해당 대외활동 참여자 및 기업 댓글 리스트
    path(
        "company/program/<int:activity_id>/comment/",
        CompanyApplicantCommentListView.as_view(),
        name="company-applicant-comment",
    ),
    # v 활동관리/활동1/소통 댓글창/등록: 기업 댓글 등록
    path(
        "company/program/<int:activity_id>/comment/create/",
        CompanyApplicantCommentCreateView.as_view(),
        name="company-applicant-comment-create",
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
    # N: 등록된 과제/과제 제출자 --
    path(
        "company/program/assignment/<int:assignment_id>/submit/",
        CompanyProgramAssignmentSubmitListView.as_view(),
        name="company-assignment-submit-list",
    ),
    # N: 등록된 과제/과제 제출자/제출 내용 --
    path(
        "company/program/assignment/<int:assignment_id>/submit/<int:pk>/",
        CompanyProgramAssignmentSubmitDetailView.as_view(),
        name="company-assignment-submit-detail",
    ),
    # R: 활동관리/활동1/학생1/과제: 과제 마감기한 연장 => db구조에 따른 로직 변경
    path(
        "company/program/assignment/<int:pk>/extend/",
        CompanyProgramAssignmentDurationExtendView.as_view(),
        name="company-program-assignment-duration-extend",
    ),
    # R: 활동관리/활동1/학생1/과제/수정요구: 과제 수정요구(1,2차) => db구조에 따른 로직 변경
    path(
        "company/program/assignment/<int:pk>/revise/",
        CompanyProgramAssignmentRevisionView.as_view(),
        name="company-program-assignment-revise",
    ),
    # R: 활동관리/활동1/학생1/과제/최종 승인: 과제 최종승인 => db구조에 따른 로직 변경
    path(
        "company/program/assignment/<int:pk>/approve/",
        CompanyProgramAssignmentApprovalView.as_view(),
        name="company-program-assignment-approve",
    ),
]
