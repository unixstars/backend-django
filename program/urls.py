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
    CompanyProgramListView,
    CompanyProgramDetailView,
    CompanyProgramApplicantDetailView,
    CompanyProgramApplicantWarningView,
    CompanyProgramWarningCreateView,
    CompanyProgramNoticeDetailView,
    CompanyProgramNoticeCreateView,
    CompanyProgramNoticeCommentCreateView,
    CompanyProgramAssignmentDetailView,
    CompanyProgramAssignmentCreateView,
    CompanyProgramAssignmentCommentCreateView,
    CompanyProgramAssignmentDurationExtendView,
    CompanyProgramAssignmentRevisionView,
    CompanyProgramAssignmentApprovalView,
)

urlpatterns = [
    ##학생
    # v 나의활동: 진행중,완료활동 리스트
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
    # v 나의활동/활동1/경고: 받은 경고 리스트
    path(
        "student/program/<int:program_id>/warning/",
        ProgramWarningView.as_view(),
        name="student-program-warning",
    ),
    # v 나의활동/활동1/공지: 공지
    path(
        "student/program/<int:program_id>/notice/<int:pk>/",
        NoticeDetailView.as_view(),
        name="student-program-notice",
    ),
    # v (학생,기업) 공지 댓글 리스트
    path(
        "notice/<int:notice_id>/comment/",
        NoticeCommentListView.as_view(),
        name="notice-comment-list",
    ),
    # v 나의활동/활동1/공지/댓글 작성: 공지 댓글 작성
    path(
        "student/notice/<int:notice_id>/comment/create/",
        NoticeCommentCreateView.as_view(),
        name="notice-comment-create",
    ),
    # v 나의활동/활동1/공지/공지 확인: 공지 확인 버튼
    path(
        "student/notice/<int:pk>/check/",
        NoticeCheckUpdateView.as_view(),
        name="notice-check",
    ),
    # v 나의활동/활동1/과제: 과제
    path(
        "student/program/<int:program_id>/assignment/<int:pk>/",
        AssignmentDetailView.as_view(),
        name="student-program-assignment",
    ),
    # v (학생,기업) 과제 댓글 리스트
    path(
        "assignment/<int:assignment_id>/comment/",
        AssignmentCommentListView.as_view(),
        name="assignment-comment-list",
    ),
    # v 나의활동/활동1/과제/댓글 작성: 과제 댓글 작성
    path(
        "student/assignment/<int:assignment_id>/comment/create/",
        AssignmentCommentCreateView.as_view(),
        name="assignment-comment-create",
    ),
    # v 나의활동/활동1/과제/과제제출: 과제 제출 버튼
    path(
        "student/assignment/<int:assignment_id>/submit/",
        SubmitCreateView.as_view(),
        name="assignment-submit",
    ),
    # v 나의활동/활동1/과제/수정: 과제 수정
    path(
        "student/assignment/<int:assignment_id>/submit/update/",
        SubmitUpdateView.as_view(),
        name="assignment-submit-update",
    ),
    ##기업
    # v 활동관리: 진행중, 완료활동 리스트
    path(
        "company/program/",
        CompanyProgramListView.as_view(),
        name="company-program-list",
    ),
    # v 활동관리/활동1: 활동1 참여자 리스트
    path(
        "company/program/<int:pk>/",
        CompanyProgramDetailView.as_view(),
        name="company-program-detail",
    ),
    # v 활동관리/활동1/학생1: 공지,과제 리스트
    path(
        "company/program/<int:activity_id>/applicant/<int:pk>/",
        CompanyProgramApplicantDetailView.as_view(),
        name="company-program-applicant-detail",
    ),
    # v 활동관리/활동1/학생1/경고: 부여한 경고 리스트
    path(
        "company/program/<int:activity_id>/applicant/<int:pk>/warning/",
        CompanyProgramApplicantWarningView.as_view(),
        name="company-program-applicant-warning",
    ),
    # v 활동관리/활동1/학생1/경고/경고하기: 경고 부여하기
    path(
        "company/program/applicant/<int:applicant_id>/warning/create/",
        CompanyProgramWarningCreateView.as_view(),
        name="company-program-applicant-warning-create",
    ),
    # v 활동관리/활동1/학생1/공지: 공지
    path(
        "company/program/applicant/<int:applicant_id>/notice/<int:pk>/",
        CompanyProgramNoticeDetailView.as_view(),
        name="company-program-applicant-notice-detail",
    ),
    # v 활동관리/활동1/학생1/공지/공지 작성: 공지 작성
    path(
        "company/program/applicant/<int:applicant_id>/notice/create/",
        CompanyProgramNoticeCreateView.as_view(),
        name="company-program-applicant-notice-create",
    ),
    # v 활동관리/활동1/학생1/공지/댓글 작성: 공지 댓글 작성
    path(
        "company/program/notice/<int:notice_id>/comment/create/",
        CompanyProgramNoticeCommentCreateView.as_view(),
        name="company-program-notice-comment-create",
    ),
    # v 활동관리/활동1/학생1/과제: 과제
    path(
        "company/program/applicant/<int:applicant_id>/assignment/<int:pk>/",
        CompanyProgramAssignmentDetailView.as_view(),
        name="company-program-assignment-detail",
    ),
    # v 활동관리/활동1/학생1/과제/과제 작성: 과제 작성
    path(
        "company/program/applicant/<int:applicant_id>/assignment/create/",
        CompanyProgramAssignmentCreateView.as_view(),
        name="company-program-assignment-create",
    ),
    # v 활동관리/활동1/학생1/과제/댓글 작성: 과제 댓글 작성
    path(
        "company/program/assignment/<int:assignment_id>/comment/create/",
        CompanyProgramAssignmentCommentCreateView.as_view(),
        name="company-program-assignment-comment-create",
    ),
    # v 활동관리/활동1/학생1/과제: 과제 마감기한 연장
    path(
        "company/program/assignment/<int:pk>/extend/",
        CompanyProgramAssignmentDurationExtendView.as_view(),
        name="company-program-assignment-duration-extend",
    ),
    # v 활동관리/활동1/학생1/과제/수정요구: 과제 수정요구(1,2차)
    path(
        "company/program/assignment/<int:pk>/revise/",
        CompanyProgramAssignmentRevisionView.as_view(),
        name="company-program-assignment-revise",
    ),
    # 활동관리/활동1/학생1/과제/최종 승인: 과제 최종승인
    path(
        "company/program/assignment/<int:pk>/approve/",
        CompanyProgramAssignmentApprovalView.as_view(),
        name="company-program-assignment-approve",
    ),
]
