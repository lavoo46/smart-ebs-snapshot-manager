───────────────────────────────────────────────
☁️ Smart EBS Snapshot Manager
───────────────────────────────────────────────
AWS EC2 EBS 스냅샷을 자동으로 생성·삭제·보존하는
클라우드 기반 서버리스(Serverless) 백업 관리 시스템입니다.

이 프로젝트는 AWS Lambda, API Gateway, DynamoDB, S3, CloudFront 를 활용하여
자동화된 백업 관리 및 정책 기반 운영을 제공합니다.

───────────────────────────────────────────────
📘 프로젝트 개요
───────────────────────────────────────────────
프로젝트명 : Smart EBS Snapshot Manager
개발 목적 : EC2 EBS 볼륨의 스냅샷을 자동 생성 및 삭제하여 관리자의 수동 작업 최소화
형태     : AWS 클라우드 서비스 기반 서버리스 아키텍처
사용 언어 : Python (3.9), TypeScript, HTML, CSS, JavaScript

───────────────────────────────────────────────
⚙️ 주요 기능
───────────────────────────────────────────────
📸 스냅샷 생성        → Volume ID 입력 후 EBS 스냅샷 자동 생성
🗑️ 스냅샷 삭제        → Snapshot ID 입력 후 삭제
📋 스냅샷 목록 조회    → DynamoDB 에 저장된 스냅샷 목록 표시
🔄 상태 동기화         → 실제 AWS 스냅샷 상태와 DB 자동 동기화
⏱️ Retention 정책     → 설정된 보존 기간 경과 시 자동 삭제
🧩 정책 추가 및 수정   → 백업 주기 및 보존일 설정 관리
💻 웹 대시보드         → CloudFront + S3 기반 시각화 UI 제공

───────────────────────────────────────────────
🧱 시스템 아키텍처
───────────────────────────────────────────────
사용자 브라우저
   │
   ▼
CloudFront (Dashboard)
   ├─ 정적 파일 로드 (S3 Hosting: index.html, style.css)
   └─ HTTPS 통신
   │
   ▼
Amazon API Gateway
   └─ Lambda Functions 호출 (Python 기반)
         ├─ create_snapshot.py      → EBS 스냅샷 생성
         ├─ delete_snapshot.py      → 스냅샷 삭제
         ├─ list_snapshots.py       → 목록 조회
         ├─ create_policy.py        → 정책 생성
         ├─ update_policy.py        → 정책 수정
         └─ list_policies.py        → 정책 조회
   │
   ▼
DynamoDB
   ├─ 스냅샷 메타데이터 저장
   └─ 정책/상태 데이터 관리
   │
   ▼
AWS EC2
   └─ 실제 EBS 스냅샷 생성 및 삭제 수행
   │
   ▼
EventBridge / CloudWatch
   └─ Lambda 자동 트리거
      (정책 기반 주기적 상태 동기화 및 보존 만료 삭제)

요약:
사용자 → CloudFront Dashboard → API Gateway → Lambda → DynamoDB / EC2
자동 트리거 → EventBridge (정책 기반 실행)

───────────────────────────────────────────────
📂 폴더 구조
───────────────────────────────────────────────
smart-ebs-snapshot-manager/
├── bin/
│   └── smart-ebs-snapshot-manager.ts             # CDK 진입점
├── lib/
│   └── smart-ebs-snapshot-manager-stack.ts       # AWS 리소스 스택 정의
├── lambda/
│   ├── api/                                     # API Gateway 연동 함수
│   │   ├── create_snapshot.py
│   │   ├── delete_snapshot.py
│   │   ├── list_snapshots.py
│   │   ├── create_policy.py
│   │   ├── update_policy.py
│   │   └── list_policies.py
│   ├── snapshot_create/handler.py               # 자동 스냅샷 생성
│   ├── snapshot_retention/handler.py            # 보존기간 만료 삭제
│   └── snapshot_state_sync/handler.py           # 상태 동기화
├── web/dashboard/
│   ├── index.html                               # 웹 대시보드
│   └── style.css
├── test/
│   └── smart-ebs-snapshot-manager.test.ts
├── package.json
├── cdk.json
└── README.md

───────────────────────────────────────────────
🧩 기술 스택
───────────────────────────────────────────────
인프라 관리     : AWS CDK (TypeScript)
서버리스 함수   : AWS Lambda (Python 3.9)
API 관리        : Amazon API Gateway
데이터베이스     : DynamoDB
웹 호스팅       : Amazon S3
CDN 및 보안     : CloudFront + HTTPS
자동 실행       : EventBridge / CloudWatch
UI 구성         : HTML / CSS / JavaScript

───────────────────────────────────────────────
🚀 배포 및 실행 가이드
───────────────────────────────────────────────
[1] 환경 설정
    npm install
    aws configure

[2] CDK 부트스트랩 (최초 1회)
    cdk bootstrap

[3] 스택 배포
    cdk deploy

[4] 웹 대시보드 접속
    CloudFront 배포 주소 또는 S3 정적 웹사이트 엔드포인트로 이동
    예: https://d1hr5wjb7cgzay.cloudfront.net

───────────────────────────────────────────────
🌐 웹 대시보드 기능
───────────────────────────────────────────────
• 스냅샷 생성 : Volume ID 입력 → [생성]
• 스냅샷 삭제 : Snapshot ID 입력 → [삭제]
• 정책 관리   : 보존 기간 및 이름 설정
• 실시간 조회 : [새로고침] 버튼으로 AWS 상태 동기화

───────────────────────────────────────────────
🧾 추가 정보
───────────────────────────────────────────────
배포 유형      : Serverless (CloudFormation 스택)
코드 기반      : TypeScript + Python 핸들러
UI 구성        : CloudFront + S3 정적 대시보드
데이터 관리    : DynamoDB 테이블 자동 관리
자동 실행 주기 : EventBridge 규칙 기반 (예: 매일 자정)

───────────────────────────────────────────────
📄 라이선스
───────────────────────────────────────────────
이 프로젝트는 MIT 라이선스를 따릅니다.
© 2025 Smart EBS Snapshot Manager Team
───────────────────────────────────────────────
