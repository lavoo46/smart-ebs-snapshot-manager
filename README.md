# ☁️ Smart EBS Snapshot Manager

> AWS의 EC2 EBS 스냅샷을 자동으로 생성, 삭제, 보존 정책에 따라 관리하는 **클라우드 기반 백업 자동화 시스템**  
> 이 프로젝트는 AWS Lambda, API Gateway, DynamoDB, S3, CloudFront를 활용한 **서버리스(Serverless)** 구조로 제작되었습니다.

---

## 🎯 프로젝트 개요

- **프로젝트명:** Smart EBS Snapshot Manager  
- **개발 목적:**  
  EC2 인스턴스의 EBS 볼륨 백업(스냅샷)을 자동으로 생성하고, 일정 기간 이후 자동 삭제하는 기능을 통해  
  관리자의 수동 작업을 최소화하고 백업 효율을 높이는 것을 목표로 함.  
- **형태:** AWS 클라우드 서비스 기반의 서버리스 시스템  
- **사용 언어:** Python, TypeScript, HTML, CSS, JavaScript  

---

## ⚙️ 주요 기능

| 기능 구분 | 설명 |
|------------|------|
| 📸 **스냅샷 생성** | 입력한 Volume ID로 EBS 스냅샷 생성 |
| 🗑️ **스냅샷 삭제** | Snapshot ID를 입력해 스냅샷 삭제 |
| 📋 **스냅샷 목록 조회** | DynamoDB에 저장된 스냅샷 목록 표시 |
| 🔄 **상태 동기화** | 실제 AWS 스냅샷 상태와 DB 데이터 자동 동기화 |
| ⏱️ **Retention 정책** | 설정된 기간이 지난 스냅샷 자동 삭제 |
| 🧩 **정책 추가 및 수정** | 백업 주기 및 보존일 관리 |
| 💻 **웹 대시보드 제공** | 시각적으로 스냅샷 현황 및 정책 관리 가능 (CloudFront + S3 기반) |

---

## 🧱 시스템 구조

```mermaid
graph TD
A[사용자 브라우저] -->|HTTPS| B[CloudFront Dashboard]
B -->|정적 파일 로드| C[S3 Hosting (index.html)]
B -->|API 요청| D[API Gateway]
D --> E[AWS Lambda Functions]
E -->|데이터 저장| F[DynamoDB]
E -->|EBS 스냅샷 제어| G[AWS EC2]
E -->|자동 트리거| H[EventBridge (주기 실행)]
📁 폴더 구조
bash
코드 복사
smart-ebs-snapshot-manager/
├── bin/                            # CDK 진입점
│   └── smart-ebs-snapshot-manager.ts
├── lib/                            # AWS 리소스 스택 정의
│   └── smart-ebs-snapshot-manager-stack.ts
├── lambda/                         # Lambda 함수 (Python)
│   ├── api/                        # API Gateway와 연결된 함수들
│   │   ├── create_snapshot.py
│   │   ├── delete_snapshot.py
│   │   ├── list_snapshots.py
│   │   ├── create_policy.py
│   │   ├── update_policy.py
│   │   └── list_policies.py
│   ├── snapshot_create/handler.py  # 자동 스냅샷 생성
│   ├── snapshot_retention/handler.py # 보존기간 만료 스냅샷 삭제
│   └── snapshot_state_sync/handler.py # 스냅샷 상태 동기화
├── web/dashboard/                  # 웹 대시보드 (S3에 업로드)
│   ├── index.html
│   └── style.css
├── test/                           # CDK 테스트 코드
│   └── smart-ebs-snapshot-manager.test.ts
├── package.json
├── cdk.json
└── README.md
🛠️ 사용 기술
구분	기술
인프라 관리	AWS CDK (TypeScript)
서버리스 함수	AWS Lambda (Python 3.9)
API 관리	Amazon API Gateway
데이터베이스	DynamoDB
웹 호스팅	Amazon S3
CDN 및 HTTPS	CloudFront
자동 실행	EventBridge / CloudWatch
UI 구성	HTML, CSS, JavaScript

🚀 실행 방법
1️⃣ 환경 설정
bash
코드 복사
npm install
aws configure
2️⃣ CDK 부트스트랩 (최초 1회)
bash
코드 복사
cdk bootstrap
3️⃣ 스택 배포
bash
코드 복사
cdk deploy
4️⃣ 웹 대시보드 접속
S3 또는 CloudFront 배포 도메인 주소로 접속

예: https://d1hr5wjb7cgzay.cloudfront.net

🌐 웹 대시보드 기능
스냅샷 생성: Volume ID 입력 후 [생성] 클릭

스냅샷 삭제: Snapshot ID 입력 후 [삭제] 클릭

정책 추가/수정: 백업 보존 기간과 이름 설정

실시간 조회: [새로고침] 버튼으로 최신 상태 확인
