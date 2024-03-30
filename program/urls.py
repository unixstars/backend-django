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
    CompanyProgramListView,
    CompanyProgramDetailView,
    CompanyProgramStartView,
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
    # N: 나의활동/활동1/소통댓글창 : 대외활동 기업 및 참여자 댓글 반환
    path(
        "student/program/<int:program_id>/comment/",
        ApplicantCommentListView.as_view(),
        name="student-program-comment",
    ),
    # N: 나의활동/활동1/소통댓글창/등록 : 학생 댓글 등록
    path(
        "student/program/<int:program_id>/comment/create/",
        ApplicantCommentCreateView.as_view(),
        name="student-program-comment-create",
    ),
    # R: 나의활동/활동1/공지: 공지 => db구조에 따른 로직 변경, 공지 체크, 댓글 없어짐
    path(
        "student/program/<int:program_id>/notice/<int:pk>/",
        NoticeDetailView.as_view(),
        name="student-program-notice",
    ),
    # D: (학생,기업) 공지 댓글 리스트
    path(
        "notice/<int:notice_id>/comment/",
        NoticeCommentListView.as_view(),
        name="notice-comment-list",
    ),
    # D: 나의활동/활동1/공지/댓글 작성: 공지 댓글 작성
    path(
        "student/notice/<int:notice_id>/comment/create/",
        NoticeCommentCreateView.as_view(),
        name="notice-comment-create",
    ),
    # D: 나의활동/활동1/공지/공지 확인: 공지 확인 버튼
    path(
        "student/notice/<int:pk>/check/",
        NoticeCheckUpdateView.as_view(),
        name="notice-check",
    ),
    # R: 나의활동/활동1/과제: 과제 => db구조에 따른 로직 변경, 공지 체크, 댓글 없어짐
    path(
        "student/program/<int:program_id>/assignment/<int:pk>/",
        AssignmentDetailView.as_view(),
        name="student-program-assignment",
    ),
    # D: (학생,기업) 과제 댓글 리스트
    path(
        "assignment/<int:assignment_id>/comment/",
        AssignmentCommentListView.as_view(),
        name="assignment-comment-list",
    ),
    # D: 나의활동/활동1/과제/댓글 작성: 과제 댓글 작성
    path(
        "student/assignment/<int:assignment_id>/comment/create/",
        AssignmentCommentCreateView.as_view(),
        name="assignment-comment-create",
    ),
    # R: 나의활동/활동1/과제/과제제출: 과제 제출 버튼 => db구조에 따른 로직 변경
    path(
        "student/assignment/<int:assignment_id>/submit/",
        SubmitCreateView.as_view(),
        name="assignment-submit",
    ),
    # R: 나의활동/활동1/과제/수정: 과제 수정 => db구조에 따른 로직 변경
    path(
        "student/assignment/<int:assignment_id>/submit/update/",
        SubmitUpdateView.as_view(),
        name="assignment-submit-update",
    ),
    # N: 과제/다른사람 제출물 : 해당 과제 다른 참여자 과제 제목 리스트
    # N: 과제/다른사람제출물/사람1 : 사람1 과제 내용
    ##기업
    # 활동관리: 진행중, 완료활동 리스트
    path(
        "company/program/",
        CompanyProgramListView.as_view(),
        name="company-program-list",
    ),
    # D: 활동관리/활동1: 활동1 참여자 리스트
    path(
        "company/program/<int:pk>/",
        CompanyProgramDetailView.as_view(),
        name="company-program-detail",
    ),
    # 활동관리/활동1/활동 시작: 대외활동 시작
    path(
        "company/program/<int:pk>/start/",
        CompanyProgramStartView.as_view(),
        name="company-program-start",
    ),
    # N: 활동관리/활동1/소통 댓글창: 해당 대외활동 참여자 및 기업 댓글 리스트
    # N: 활동관리/활동1/소통 댓글창/등록: 기업 댓글 등록
    # R: 활동관리/활동1: 공지,과제 리스트 => db구조에 따른 로직 변경
    path(
        "company/program/<int:activity_id>/applicant/<int:pk>/",
        CompanyProgramApplicantDetailView.as_view(),
        name="company-program-applicant-detail",
    ),
    # R: 활동관리/활동1/학생1/경고: 부여한 경고 리스트 => 활동관리/경고 부여로 내용 변경
    path(
        "company/program/<int:activity_id>/applicant/<int:pk>/warning/",
        CompanyProgramApplicantWarningView.as_view(),
        name="company-program-applicant-warning",
    ),
    # 활동관리/활동1/학생1/경고/경고하기: 경고 부여하기
    path(
        "company/program/applicant/<int:applicant_id>/warning/create/",
        CompanyProgramWarningCreateView.as_view(),
        name="company-program-applicant-warning-create",
    ),
    # R: 활동관리/활동1/공지: 공지 => db구조에 따른 로직 변경
    path(
        "company/program/applicant/<int:applicant_id>/notice/<int:pk>/",
        CompanyProgramNoticeDetailView.as_view(),
        name="company-program-applicant-notice-detail",
    ),
    # R: 활동관리/활동1/공지/공지 작성: 공지 작성 => db구조에 따른 로직 변경
    path(
        "company/program/applicant/<int:applicant_id>/notice/create/",
        CompanyProgramNoticeCreateView.as_view(),
        name="company-program-applicant-notice-create",
    ),
    # D: 활동관리/활동1/학생1/공지/댓글 작성: 공지 댓글 작성
    path(
        "company/program/notice/<int:notice_id>/comment/create/",
        CompanyProgramNoticeCommentCreateView.as_view(),
        name="company-program-notice-comment-create",
    ),
    # R: 활동관리/활동1/학생1/과제: 과제 => db구조에 따른 로직 변경
    path(
        "company/program/applicant/<int:applicant_id>/assignment/<int:pk>/",
        CompanyProgramAssignmentDetailView.as_view(),
        name="company-program-assignment-detail",
    ),
    # R: 활동관리/활동1/학생1/과제/과제 작성: 과제 작성 => db구조에 따른 로직 변경
    path(
        "company/program/applicant/<int:applicant_id>/assignment/create/",
        CompanyProgramAssignmentCreateView.as_view(),
        name="company-program-assignment-create",
    ),
    # D: 활동관리/활동1/학생1/과제/댓글 작성: 과제 댓글 작성
    path(
        "company/program/assignment/<int:assignment_id>/comment/create/",
        CompanyProgramAssignmentCommentCreateView.as_view(),
        name="company-program-assignment-comment-create",
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
