# ☁️ Smart EBS Snapshot Manager

> **자동화된 AWS EBS 스냅샷 관리 시스템**  
> EC2 EBS 볼륨의 스냅샷을 자동으로 생성·삭제·보존하는 **서버리스(Serverless)** 백업 관리 솔루션입니다.  
> AWS Lambda, API Gateway, DynamoDB, S3, CloudFront를 활용해 완전 자동화된 클라우드 운영 환경을 구현합니다.

---

## 📘 프로젝트 개요

| 항목 | 내용 |
|------|------|
| **프로젝트명** | Smart EBS Snapshot Manager |
| **목적** | EC2 EBS 볼륨의 스냅샷을 자동으로 생성하고 보존 기간 이후 자동 삭제하여 운영자의 수동 작업 감소 및 백업 효율 향상 |
| **형태** | AWS 클라우드 서비스 기반 서버리스 아키텍처 |
| **사용 언어** | Python (3.9), TypeScript, HTML, CSS, JavaScript |

---

## ⚙️ 주요 기능

| 기능 | 설명 |
|------|------|
| 📸 **스냅샷 생성** | 입력한 Volume ID로 EBS 스냅샷 생성 |
| 🗑️ **스냅샷 삭제** | Snapshot ID 입력 후 스냅샷 삭제 |
| 📋 **스냅샷 목록 조회** | DynamoDB에 저장된 스냅샷 목록 표시 |
| 🔄 **상태 동기화** | 실제 AWS 스냅샷 상태와 DB 데이터 자동 동기화 |
| ⏱️ **Retention 정책** | 설정된 기간이 지난 스냅샷 자동 삭제 |
| 🧩 **정책 추가 및 수정** | 백업 주기 및 보존일 관리 |
| 💻 **웹 대시보드 제공** | CloudFront + S3 기반의 UI로 스냅샷 현황 시각화 |

---

## 🧱 시스템 아키텍처

```mermaid
graph TD
A[사용자 브라우저] -->|HTTPS| B[CloudFront Dashboard]
B -->|정적 파일 로드| C[S3 Hosting (index.html)]
B -->|API 요청| D[Amazon API Gateway]
D --> E[AWS Lambda Functions]
E -->|데이터 저장| F[DynamoDB]
E -->|EBS 제어| G[AWS EC2]
E -->|자동 트리거| H[EventBridge / CloudWatch]

🧩 기술 스택
구분	기술
인프라 관리	AWS CDK (TypeScript)
서버리스 함수	AWS Lambda (Python 3.9)
API 관리	Amazon API Gateway
데이터베이스	DynamoDB
웹 호스팅	Amazon S3
CDN 및 보안	CloudFront + HTTPS
자동 실행	EventBridge / CloudWatch
UI 구성	HTML / CSS / JavaScript
🚀 배포 및 실행 가이드
1️⃣ 환경 설정
npm install
aws configure

2️⃣ CDK 부트스트랩 (최초 1회)
cdk bootstrap

3️⃣ 스택 배포
cdk deploy

4️⃣ 웹 대시보드 접속

CloudFront 배포 주소 또는 S3 정적 웹사이트 엔드포인트로 이동
예시: https://d1hr5wjb7cgzay.cloudfront.net

🌐 웹 대시보드 기능

스냅샷 생성 : Volume ID 입력 → [생성]

스냅샷 삭제 : Snapshot ID 입력 → [삭제]

정책 관리 : 보존 기간 및 이름 설정

실시간 조회 : [새로고침] 버튼으로 AWS 상태 동기화

🧾 추가 정보
항목	내용
배포 유형	Serverless (CloudFormation 스택)
코드 기반	TypeScript + Python 핸들러
UI 구성	CloudFront + S3 정적 대시보드
데이터 관리	DynamoDB 테이블 자동 관리
자동 실행 주기	EventBridge 규칙 기반 (예: 매일 자정)