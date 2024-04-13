# 대외활동 관리 플랫폼 '유니스타(unistar)' 백엔드

## 소개 및 주요 기능

### 소개

<p align="right">
  <img src="/readme_images/unistar_intro.PNG" alt="유니스타 소개 1" style="width: 30%;margin-right:1%;">
  <img src="/readme_images/unistar_intro2.PNG" alt="유니스타 소개 2" style="width: 30%;margin-right:1%;">
  <img src="/readme_images/unistar_intro3.PNG" alt="유니스타 소개 3" style="width: 30%;margin-right:1%;">
</p>

- 대외활동 관리 플랫폼 유니스타 입니다!
- 기존 대외활동 플랫폼에서 제기되는 문제인 부실한 관리를 공지 및 과제 기능으로 보완할 수 있습니다.
- 대외활동을 잘 모르는 기업들도 체계적인 시스템 하에 대외활동 진행이 가능합니다.
- 학생에겐 실무 경험을, 기업에겐 적은 가격에 홍보 테스트를.
- 디자인 업데이트 및 기능 업데이트 예정(6월)

### 기업 측 주요 기능(기존 버전, 사용자 피드백 후 업데이트 중)

- 로그인/회원가입: 국세청 api 법인기업 인증
- 대외활동 게시글 작성(모집): 대외활동 게시글을 작성 후 학생 모집
- 지원자 관리: 받은 지원서를 합격/불합격 시키는 기능
- 참여자 관리: 참여자에게 경고 부여, 공지/과제 부여
- 과제 관리: 제출된 과제 파일 수정 요청 및 최종 승인
- 공지,과제 댓글: 참여자와 소통

### 학생 측 주요 기능(기존 버전, 사용자 피드백 후 업데이트 중)

- 로그인/회원가입: 구글,네이버,카카오,애플 소셜 로그인
- 프로필,포트폴리오 작성
- 대외활동 지원: 지원서 작성
- 과제 제출(파일 제출): 기업이 최대 3번까지 수정 요구 가능, 수정요구가 되면 제출 가능
- 공지,과제 댓글: 기업과 소통

## 문서

- API 문서(업데이트 이전 버전): https://www.notion.so/API-1-ac5069b51c8a4433bdac9b1c820e04d1?pvs=4
- 디자인 와이어프레임(업데이트 이전 버전, 경력 10년 디자이너 컨택 완료 및 작업 예정): https://www.figma.com/file/DEIMcmXQbXg4jADLmW3UZK/%EC%99%80%EC%9D%B4%EC%96%B4%ED%94%84%EB%A0%88%EC%9E%84?type=design&node-id=3670%3A5445&mode=design&t=xW4LLMbPGCY7aRqw-1

## ERD(Entity Relationship Diragram)

![유니스타 ERD](/readme_images/UNISTAR_2.0.png)

- 장고 유저 모델은 단일 모델이기에, 유저 모델을 식별관계로 확장하여 학생,기업유저를 설정
- 데이터베이스화 및 악성유저 밴을 위해 로그인이벤트(시간 및 ip) 수집
- 대외활동 모집 게시글: 최대 3개까지 대외활동을 모집할 수 있음
- 학생유저의 경우 프로필이 필수(OneToOne), 포트폴리오는 여러개를 가질 수 있음
- 기업은 학생의 프로필을 보고 여러 개의 지원제안을 보낼 수 있고, 학생은 여러 기업으로부터 지원제안을 받을 수 있음
- 학생은 대외활동 게시글 여러 개를 스크랩 할 수 있고, 대외활동 게시글은 여러 명의 학생으로부터 스크랩을 받을 수 있음
- 학생이 대외활동에 지원을 할 경우 지원서를 작성해야 함. 지원서를 생성한 경우 기업과 학생 간 소통 댓글창이 만들어짐
- 지원한 학생 중 합격한 학생의 경우 합격자가 생성됨. 합격자는 대외활동 진행상태와 주차를 포함하는 프로그램의 역할
- 합격자(대외활동 진행 학생)의 대외활동이 부실한 경우 기업은 학생에게 경고 부여 가능
- 합격자의 경우 기업 대외활동과 합격자 간 댓글로 소통 가능
- 대외활동과 합격자 간에 공지와 과제가 존재. 공지 과제는 주차별로 기업이 등록 가능.
- 앱 버전 관리를 위해 RemoteConfig 존재.

## Infrastucture

- AWS EC2, AWS S3(Using CDN), AWS RDS(MySQL 8.0)
- uwsgi, nginx
- 개발 서버와 프로덕션 서버로 분리하여 사용 중

## 프로젝트 구조

### config/settings.py

- 개발 서버와 프로덕트 서버 설정 분리
- auth로 장고 기본 백엔드&allauth 백엔드 사용
- throttle로 ip에 따른 사용자별 api 횟수제한
- cronjob: 시간 지난 로그 삭제, 대외활동 주차 업데이트(7일), 시간 지난 토큰 삭제, 기간 만료된 게시글 마감으로 설정
- logging: 클라이언트 에러 로그, 서버 에러 로그, api 10000회 이상 요청 ip 기록(디도스 발생 후 추가함)
- 인증 방식 jwt token 사용(dj-rest-auth)
- DB: AWS RDS(MySQL 8.0), Media: AWS S3 bucket/이미지 캐싱 CDN(AWS CloudFront) 사용
- static: 장고 admin을 위한 기본 static 파일(EC2 내 존재)
- 파일 업로드 크기 제한(300MB)

### config/

- uwsgi: 소켓과 ec2 내 가상환경 실행 등 명령어 자동화
- nginx: 80번 포트(http)를 받으며, 443(https)의 경우 aws 로드밸런서 redirect 이용

### app

- activity: 학생이 대외활동에 지원하기 전, 로그인 전 게시글
- api: RemoteConfig, middleware, hash fuction 등 공통적으로 쓰이는 실행파일
- authentication; 학생(소셜 로그인), 기업(법인 인증), 관리자 인증
- program: 학생이 대외활동에 지원한 후, 공지/과제/경고 등
- user: 유저 모델, 학생 프로필, 포트폴리오 등

### 기타

- migration_script: 1.0에서 2.0으로 데이터 구조를 바꾸는 업데이트 과정에서 작성된 마이그레이션 파일
- readme_images: README.md에 사용되는 이미지 파일
- data.json: 초기 db 설정 과정 중 테스트 데이터
- manage.py: 파이썬 실행 파일
- mystorages.py: aws s3 bucket 연결 과정에서 사용되는 boto3 클래스
- pipfile, pipfile.lock: 패키지 버전 관리
