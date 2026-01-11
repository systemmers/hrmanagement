# HR Management System - API Schema

본 문서는 HR Management 시스템의 모든 API 엔드포인트를 정리한 문서입니다.

**생성일**: 2025-12-16
**최종 업데이트**: 2026-01-11
**프로젝트**: D:/projects/hrmanagement
**Python**: Flask Blueprint 기반 (도메인 중심 아키텍처)

---

## 목차

1. [인증 및 세션](#1-인증-및-세션)
2. [직원 관리](#2-직원-관리)
3. [계약 관리](#3-계약-관리)
4. [법인 관리](#4-법인-관리)
5. [개인 계정](#5-개인-계정)
6. [프로필 관리](#6-프로필-관리)
7. [분류 옵션](#7-분류-옵션)
8. [조직 관리](#8-조직-관리)
9. [알림 시스템](#9-알림-시스템)
10. [감사 로그](#10-감사-로그)
11. [동기화](#11-동기화)
12. [계정 설정](#12-계정-설정)
13. [첨부파일 관리](#13-첨부파일-관리)
14. [명함 관리](#14-명함-관리)
15. [기타](#15-기타)

---

## 1. 인증 및 세션

### Blueprint: `auth_bp` (prefix: `/auth`)

| HTTP | 엔드포인트 | 인증 | 역할 | 설명 |
|------|-----------|------|------|------|
| GET  | `/auth/login` | - | - | 로그인 페이지 |
| POST | `/auth/login` | - | - | 로그인 처리 |
| GET  | `/auth/register` | - | - | 회원가입 유형 선택 |
| GET  | `/auth/logout` | - | - | 로그아웃 |
| GET  | `/auth/change-password` | 필수 | - | 비밀번호 변경 페이지 |
| POST | `/auth/change-password` | 필수 | - | 비밀번호 변경 처리 |

**Request 예시** (POST `/auth/login`):
```json
{
  "username": "testuser",
  "password": "password123"
}
```

**Response**: 세션에 `user_id`, `username`, `user_role`, `employee_id`, `account_type`, `company_id` 저장

---

## 2. 직원 관리

### Blueprint: `employees_bp` (no prefix)

#### 2.1 목록 조회

| HTTP | 엔드포인트 | 인증 | 역할 | 설명 |
|------|-----------|------|------|------|
| GET  | `/employees` | 필수 | manager/admin | 직원 목록 (계약 approved만) |
| GET  | `/employees/pending` | 필수 | manager/admin | 계약 대기 목록 |
| GET  | `/api/employees` | 필수 | manager/admin | 직원 목록 API (내보내기용) |

**Query Parameters** (`/employees`):
- `department`: 부서 필터 (다중 선택 가능)
- `position`: 직급 필터 (다중 선택 가능)
- `status`: 상태 필터 (다중 선택 가능)
- `sort`: 정렬 필드 (id, name, department, position, hireDate, status)
- `order`: 정렬 방향 (asc, desc)

**Response 예시** (`/api/employees`):
```json
{
  "success": true,
  "employees": [
    {
      "id": 1,
      "employee_number": "EMP001",
      "name": "홍길동",
      "department": "개발팀",
      "position": "대리",
      "email": "hong@example.com",
      "phone": "010-1234-5678",
      "hire_date": "2024-01-01",
      "status": "active",
      "user_id": 5,
      "user_email": "hong@example.com",
      "contract_status": "approved"
    }
  ],
  "total": 10
}
```

#### 2.2 상세 조회 및 폼

| HTTP | 엔드포인트 | 인증 | 역할 | 설명 |
|------|-----------|------|------|------|
| GET  | `/employees/<int:employee_id>` | 필수 | - | 직원 상세 정보 (employee는 본인만) |
| GET  | `/employees/new` | 필수 | manager/admin | 직원 등록 폼 |
| GET  | `/employees/<int:employee_id>/edit` | 필수 | - | 직원 수정 폼 (employee는 본인만) |
| GET  | `/employees/<int:employee_id>/edit/basic` | 필수 | - | 기본정보 수정 폼 (리다이렉트) |
| GET  | `/employees/<int:employee_id>/edit/history` | 필수 | - | 이력정보 수정 폼 (리다이렉트) |

#### 2.3 생성/수정/삭제

| HTTP | 엔드포인트 | 인증 | 역할 | 설명 |
|------|-----------|------|------|------|
| POST | `/employees` | 필수 | manager/admin | 직원 등록 (계정 동시 생성 지원) |
| POST | `/employees/<int:employee_id>/update` | 필수 | - | 직원 수정 (employee는 본인만) |
| POST | `/employees/<int:employee_id>/update/basic` | 필수 | - | 기본정보 수정 |
| POST | `/employees/<int:employee_id>/update/history` | 필수 | - | 이력정보 수정 |
| POST | `/employees/<int:employee_id>/delete` | 필수 | admin | 직원 삭제 |

**Request 예시** (POST `/employees`):
```form-data
name: "홍길동"
department: "개발팀"
position: "대리"
email: "hong@example.com"
phone: "010-1234-5678"
hire_date: "2024-01-01"
status: "active"
create_account: "true"  # 계정 동시 생성
account_username: "honggildong"
account_email: "hong@example.com"
account_password: "password123"
account_role: "employee"
```

---

## 3. 계약 관리

### Blueprint: `contracts_bp` (prefix: `/contracts`)

#### 3.1 개인/직원 계정용

| HTTP | 엔드포인트 | 인증 | 역할 | 설명 |
|------|-----------|------|------|------|
| GET  | `/contracts/my` | 필수 | personal/employee_sub | 내 계약 목록 |
| GET  | `/contracts/pending` | 필수 | personal/employee_sub | 대기 중인 계약 요청 |
| GET  | `/contracts/<int:contract_id>` | 필수 | - | 계약 상세 조회 (당사자만) |

#### 3.2 법인 계정용

| HTTP | 엔드포인트 | 인증 | 역할 | 설명 |
|------|-----------|------|------|------|
| GET  | `/contracts/company` | 필수 | corporate | 법인 계약 목록 |
| GET  | `/contracts/company/pending` | 필수 | corporate | 법인 대기 중인 요청 |
| GET  | `/contracts/request` | 필수 | corporate | 계약 요청 폼 |
| POST | `/contracts/request` | 필수 | corporate | 계약 요청 처리 |

**Request 예시** (POST `/contracts/request`):
```form-data
person_email: "person@example.com"
contract_type: "employment"
position: "대리"
department: "개발팀"
notes: "신입 개발자"
```

#### 3.3 API 엔드포인트

| HTTP | 엔드포인트 | 인증 | 역할 | 설명 |
|------|-----------|------|------|------|
| POST | `/contracts/api/<int:contract_id>/approve` | 필수 | 당사자 | 계약 승인 |
| POST | `/contracts/api/<int:contract_id>/reject` | 필수 | 당사자 | 계약 거절 |
| POST | `/contracts/api/<int:contract_id>/terminate` | 필수 | 당사자 | 계약 종료 |
| GET  | `/contracts/api/<int:contract_id>/sharing-settings` | 필수 | 개인 | 공유 설정 조회 |
| PUT  | `/contracts/api/<int:contract_id>/sharing-settings` | 필수 | 개인 | 공유 설정 업데이트 |
| GET  | `/contracts/api/<int:contract_id>/sync-logs` | 필수 | 당사자 | 동기화 로그 조회 |
| GET  | `/contracts/api/search` | 필수 | corporate | 계약 검색 |
| GET  | `/contracts/api/stats/company` | 필수 | corporate | 법인 계약 통계 |
| GET  | `/contracts/api/stats/personal` | 필수 | personal/employee_sub | 개인/직원 계약 통계 |
| POST | `/contracts/api/employee/<int:user_id>/request` | 필수 | corporate | 직원에게 계약 요청 |

**Request 예시** (POST `/contracts/api/<int:contract_id>/reject`):
```json
{
  "reason": "다른 회사에 이미 근무 중"
}
```

**Response 예시**:
```json
{
  "success": true,
  "message": "계약이 거절되었습니다.",
  "data": {
    "contract_id": 1,
    "status": "rejected"
  }
}
```

---

## 4. 법인 관리

### Blueprint: `corporate_bp` (prefix: `/corporate`)

#### 4.1 법인 회원가입 및 대시보드

| HTTP | 엔드포인트 | 인증 | 역할 | 설명 |
|------|-----------|------|------|------|
| GET  | `/corporate/register` | - | - | 법인 회원가입 페이지 |
| POST | `/corporate/register` | - | - | 법인 회원가입 처리 |
| GET  | `/corporate/dashboard` | 필수 | corporate | 법인 대시보드 |
| GET  | `/corporate/settings` | 필수 | admin | 법인 정보 설정 |
| POST | `/corporate/settings` | 필수 | admin | 법인 정보 수정 |

#### 4.2 법인 사용자 관리

| HTTP | 엔드포인트 | 인증 | 역할 | 설명 |
|------|-----------|------|------|------|
| GET  | `/corporate/users` | 필수 | admin | 법인 계정 관리 (employee_sub만) |
| GET  | `/corporate/users/add` | 필수 | admin | 사용자 추가 폼 |
| POST | `/corporate/users/add` | 필수 | admin | 사용자 추가 처리 |

#### 4.3 API 엔드포인트

| HTTP | 엔드포인트 | 인증 | 역할 | 설명 |
|------|-----------|------|------|------|
| GET  | `/corporate/api/check-business-number` | - | - | 사업자등록번호 중복 확인 |
| GET  | `/corporate/api/company/<int:company_id>` | 필수 | corporate | 법인 정보 조회 (본인만) |

**Request 예시** (POST `/corporate/register`):
```form-data
# 법인 정보
company_name: "주식회사 테스트"
business_number: "123-45-67890"
corporate_number: "110111-1234567"
representative: "대표자명"
business_type: "제조업"
business_category: "전자제품"
phone: "02-1234-5678"
company_email: "company@test.com"
address: "서울시 강남구"

# 관리자 계정
username: "admin"
email: "admin@test.com"
password: "password123"
password_confirm: "password123"
```

---

## 5. 개인 계정

### Blueprint: `personal_bp` (prefix: `/personal`)

#### 5.1 회원가입 및 대시보드

| HTTP | 엔드포인트 | 인증 | 역할 | 설명 |
|------|-----------|------|------|------|
| GET  | `/personal/register` | - | - | 개인 회원가입 페이지 |
| POST | `/personal/register` | - | - | 개인 회원가입 처리 |
| GET  | `/personal/dashboard` | 필수 | personal | 개인 대시보드 |
| GET  | `/personal/profile` | 필수 | personal | 프로필 조회 (리다이렉트) |
| GET  | `/personal/profile/edit` | 필수 | personal | 프로필 수정 폼 (리다이렉트) |
| POST | `/personal/profile/edit` | 필수 | personal | 프로필 수정 처리 |

#### 5.2 이력 관리 API

**학력 관리**

| HTTP | 엔드포인트 | 인증 | 역할 | 설명 |
|------|-----------|------|------|------|
| GET  | `/personal/education` | 필수 | personal | 학력 목록 조회 |
| POST | `/personal/education` | 필수 | personal | 학력 추가 |
| DELETE | `/personal/education/<int:education_id>` | 필수 | personal | 학력 삭제 |

**경력 관리**

| HTTP | 엔드포인트 | 인증 | 역할 | 설명 |
|------|-----------|------|------|------|
| GET  | `/personal/career` | 필수 | personal | 경력 목록 조회 |
| POST | `/personal/career` | 필수 | personal | 경력 추가 |
| DELETE | `/personal/career/<int:career_id>` | 필수 | personal | 경력 삭제 |

**자격증 관리**

| HTTP | 엔드포인트 | 인증 | 역할 | 설명 |
|------|-----------|------|------|------|
| GET  | `/personal/certificate` | 필수 | personal | 자격증 목록 조회 |
| POST | `/personal/certificate` | 필수 | personal | 자격증 추가 |
| DELETE | `/personal/certificate/<int:certificate_id>` | 필수 | personal | 자격증 삭제 |

**어학 관리**

| HTTP | 엔드포인트 | 인증 | 역할 | 설명 |
|------|-----------|------|------|------|
| GET  | `/personal/language` | 필수 | personal | 어학 목록 조회 |
| POST | `/personal/language` | 필수 | personal | 어학 추가 |
| DELETE | `/personal/language/<int:language_id>` | 필수 | personal | 어학 삭제 |

**병역 관리**

| HTTP | 엔드포인트 | 인증 | 역할 | 설명 |
|------|-----------|------|------|------|
| GET  | `/personal/military` | 필수 | personal | 병역 정보 조회 |
| POST | `/personal/military` | 필수 | personal | 병역 정보 저장/수정 |

#### 5.3 회사 인사카드 (개인 계정용)

| HTTP | 엔드포인트 | 인증 | 역할 | 설명 |
|------|-----------|------|------|------|
| GET  | `/personal/company-cards` | 필수 | personal | 계약된 회사 인사카드 목록 |
| GET  | `/personal/company-cards/<int:contract_id>` | 필수 | personal | 특정 회사 인사카드 상세 |

---

## 6. 프로필 관리

### Blueprint: `profile_bp` (prefix: `/profile`)

#### 6.1 통합 프로필

| HTTP | 엔드포인트 | 인증 | 역할 | 설명 |
|------|-----------|------|------|------|
| GET  | `/profile/` | 필수 | - | 통합 프로필 조회 (모든 계정 타입) |
| GET  | `/profile/edit` | 필수 | - | 통합 프로필 수정 폼 |
| POST | `/profile/edit` | 필수 | - | 통합 프로필 수정 처리 |

#### 6.2 섹션별 데이터 API

| HTTP | 엔드포인트 | 인증 | 역할 | 설명 |
|------|-----------|------|------|------|
| GET  | `/profile/section/<section_name>` | 필수 | - | 섹션별 데이터 조회 |
| GET  | `/profile/corporate/salary-history` | 필수 | corporate | 급여 이력 (법인 전용) |
| GET  | `/profile/corporate/promotions` | 필수 | corporate | 승진 이력 (법인 전용) |
| GET  | `/profile/corporate/evaluations` | 필수 | corporate | 평가 기록 (법인 전용) |
| GET  | `/profile/corporate/trainings` | 필수 | corporate | 교육 이력 (법인 전용) |
| GET  | `/profile/corporate/attendances` | 필수 | corporate | 근태 기록 (법인 전용) |
| GET  | `/profile/corporate/assets` | 필수 | corporate | 비품 목록 (법인 전용) |
| GET  | `/profile/corporate/family` | 필수 | corporate | 가족 정보 (법인 전용) |
| GET  | `/profile/hr-projects` | 필수 | - | 인사이력 프로젝트 목록 |
| GET  | `/profile/project-participations` | 필수 | - | 프로젝트 참여이력 목록 |
| GET  | `/profile/awards` | 필수 | - | 수상 이력 조회 |

**섹션 이름 (section_name)**:
- `basic`: 기본 정보
- `organization`: 소속 정보
- `contract`: 계약 정보
- `salary`: 급여 정보
- `benefit`: 복리후생 정보
- `insurance`: 보험 정보
- `education`: 학력 정보
- `career`: 경력 정보
- `certificate`: 자격증 정보
- `language`: 어학 정보
- `military`: 병역 정보

#### 6.3 법인 관리자 프로필

| HTTP | 엔드포인트 | 인증 | 역할 | 설명 |
|------|-----------|------|------|------|
| GET  | `/profile/admin/create` | 필수 | corporate | 법인 관리자 프로필 생성 폼 |
| POST | `/profile/admin/create` | 필수 | corporate | 법인 관리자 프로필 생성 처리 |
| GET  | `/profile/admin/edit` | 필수 | corporate_admin | 법인 관리자 프로필 수정 폼 |
| POST | `/profile/admin/edit` | 필수 | corporate_admin | 법인 관리자 프로필 수정 처리 |
| GET  | `/profile/api/admin/profile` | 필수 | corporate_admin | 법인 관리자 프로필 조회 API |
| PUT  | `/profile/api/admin/profile` | 필수 | corporate_admin | 법인 관리자 프로필 수정 API |
| GET  | `/profile/api/admin/company` | 필수 | corporate_admin | 법인 관리자 회사 정보 조회 API |

---

## 7. 분류 옵션

### Blueprint: `api_bp` (no prefix) / `classification_bp` (no prefix)

#### 7.1 조회

| HTTP | 엔드포인트 | 인증 | 역할 | 설명 |
|------|-----------|------|------|------|
| GET  | `/classification-options` | 필수 | - | 분류 옵션 관리 페이지 |
| GET  | `/api/classification-options` | 필수 | - | 분류 옵션 조회 API |

**Response 예시**:
```json
{
  "departments": ["개발팀", "영업팀", "인사팀"],
  "positions": ["사원", "대리", "과장", "차장", "부장"],
  "statuses": [
    {"value": "active", "label": "재직"},
    {"value": "inactive", "label": "퇴직"},
    {"value": "on_leave", "label": "휴직"}
  ]
}
```

#### 7.2 부서 관리

| HTTP | 엔드포인트 | 인증 | 역할 | 설명 |
|------|-----------|------|------|------|
| POST | `/api/classification-options/departments` | 필수 | admin | 부서 추가 |
| PUT  | `/api/classification-options/departments/<old_department>` | 필수 | admin | 부서 수정 |
| DELETE | `/api/classification-options/departments/<department>` | 필수 | admin | 부서 삭제 |

#### 7.3 직급 관리

| HTTP | 엔드포인트 | 인증 | 역할 | 설명 |
|------|-----------|------|------|------|
| POST | `/api/classification-options/positions` | 필수 | admin | 직급 추가 |
| PUT  | `/api/classification-options/positions/<old_position>` | 필수 | admin | 직급 수정 |
| DELETE | `/api/classification-options/positions/<position>` | 필수 | admin | 직급 삭제 |

#### 7.4 상태 관리

| HTTP | 엔드포인트 | 인증 | 역할 | 설명 |
|------|-----------|------|------|------|
| POST | `/api/classification-options/statuses` | 필수 | admin | 상태 추가 |
| PUT  | `/api/classification-options/statuses/<old_value>` | 필수 | admin | 상태 수정 |
| DELETE | `/api/classification-options/statuses/<value>` | 필수 | admin | 상태 삭제 |

---

## 8. 조직 관리

### Blueprint: `admin_bp` (prefix: `/admin`)

#### 8.1 조직 관리

| HTTP | 엔드포인트 | 인증 | 역할 | 설명 |
|------|-----------|------|------|------|
| GET  | `/admin/organizations` | 필수 | admin | 조직 관리 페이지 |
| GET  | `/admin/api/organizations` | 필수 | - | 조직 목록 API |
| GET  | `/admin/api/organizations/<int:org_id>` | 필수 | - | 조직 상세 조회 API |
| POST | `/admin/api/organizations` | 필수 | admin | 조직 생성 API |
| PUT  | `/admin/api/organizations/<int:org_id>` | 필수 | admin | 조직 수정 API |
| DELETE | `/admin/api/organizations/<int:org_id>` | 필수 | admin | 조직 비활성화 API |
| POST | `/admin/api/organizations/<int:org_id>/move` | 필수 | admin | 조직 이동 API |
| GET  | `/admin/api/organizations/<int:org_id>/children` | 필수 | - | 하위 조직 목록 API |
| GET  | `/admin/api/organizations/search` | 필수 | - | 조직 검색 API |

**Query Parameters** (`/admin/api/organizations`):
- `format`: 응답 형식 (tree, flat)

**Request 예시** (POST `/admin/api/organizations`):
```json
{
  "name": "개발1팀",
  "org_type": "team",
  "parent_id": 1,
  "code": "DEV001",
  "manager_id": 5,
  "description": "웹 개발팀"
}
```

---

## 9. 알림 시스템

### Blueprint: `notifications_bp` (prefix: `/api/notifications`)

#### 9.1 알림 조회

| HTTP | 엔드포인트 | 인증 | 역할 | 설명 |
|------|-----------|------|------|------|
| GET  | `/api/notifications` | 필수 | - | 알림 목록 조회 |
| GET  | `/api/notifications/count` | 필수 | - | 읽지 않은 알림 개수 |
| GET  | `/api/notifications/<int:notification_id>` | 필수 | - | 알림 상세 조회 |

**Query Parameters** (`/api/notifications`):
- `unread_only`: 읽지 않은 알림만 (true/false, 기본 false)
- `type`: 알림 유형 필터
- `limit`: 조회 제한 (기본 50)
- `offset`: 오프셋 (기본 0)

**Response 예시**:
```json
{
  "success": true,
  "notifications": [
    {
      "id": 1,
      "type": "contract_request",
      "title": "계약 요청",
      "message": "주식회사 테스트에서 계약을 요청했습니다.",
      "is_read": false,
      "created_at": "2024-01-01T10:00:00",
      "data": {"contract_id": 1}
    }
  ],
  "unread_count": 5,
  "limit": 50,
  "offset": 0
}
```

#### 9.2 알림 상태 관리

| HTTP | 엔드포인트 | 인증 | 역할 | 설명 |
|------|-----------|------|------|------|
| POST | `/api/notifications/<int:notification_id>/read` | 필수 | - | 알림 읽음 처리 |
| POST | `/api/notifications/read-all` | 필수 | - | 모든 알림 읽음 처리 |
| DELETE | `/api/notifications/<int:notification_id>` | 필수 | - | 알림 삭제 |

#### 9.3 알림 통계 및 설정

| HTTP | 엔드포인트 | 인증 | 역할 | 설명 |
|------|-----------|------|------|------|
| GET  | `/api/notifications/stats` | 필수 | - | 알림 통계 조회 |
| GET  | `/api/notifications/preferences` | 필수 | - | 알림 설정 조회 |
| PUT  | `/api/notifications/preferences` | 필수 | - | 알림 설정 업데이트 |
| GET  | `/api/notifications/types` | 필수 | - | 알림 유형 목록 |

**알림 유형**:
- `contract_request`: 계약 요청
- `contract_approved`: 계약 승인
- `contract_rejected`: 계약 거절
- `contract_terminated`: 계약 종료
- `data_sync`: 데이터 동기화
- `system`: 시스템 알림

---

## 10. 감사 로그

### Blueprint: `audit_bp` (prefix: `/api/audit`)

#### 10.1 로그 조회

| HTTP | 엔드포인트 | 인증 | 역할 | 설명 |
|------|-----------|------|------|------|
| GET  | `/api/audit/logs` | 필수 | admin/manager | 감사 로그 조회 (관리자용) |
| GET  | `/api/audit/logs/resource/<resource_type>/<int:resource_id>` | 필수 | admin/manager | 특정 리소스 로그 조회 |
| GET  | `/api/audit/logs/user/<int:user_id>` | 필수 | admin/manager | 특정 사용자 활동 로그 |
| GET  | `/api/audit/logs/my` | 필수 | - | 내 활동 로그 조회 |

**Query Parameters** (`/api/audit/logs`):
- `user_id`: 사용자 ID 필터
- `action`: 액션 유형 필터
- `resource_type`: 리소스 유형 필터
- `resource_id`: 리소스 ID 필터
- `status`: 상태 필터
- `start_date`: 시작 날짜 (ISO format)
- `end_date`: 종료 날짜 (ISO format)
- `limit`: 조회 제한 (기본 100)
- `offset`: 오프셋 (기본 0)

**Response 예시**:
```json
{
  "success": true,
  "logs": [
    {
      "id": 1,
      "user_id": 5,
      "username": "honggildong",
      "action": "view",
      "resource_type": "employee",
      "resource_id": 1,
      "status": "success",
      "ip_address": "127.0.0.1",
      "user_agent": "Mozilla/5.0...",
      "created_at": "2024-01-01T10:00:00",
      "details": {}
    }
  ],
  "total": 150,
  "limit": 100,
  "offset": 0
}
```

#### 10.2 통계

| HTTP | 엔드포인트 | 인증 | 역할 | 설명 |
|------|-----------|------|------|------|
| GET  | `/api/audit/stats` | 필수 | admin/manager | 감사 로그 통계 (관리자용) |
| GET  | `/api/audit/stats/company` | 필수 | admin/manager | 법인 감사 통계 |
| GET  | `/api/audit/access-summary/employee/<int:employee_id>` | 필수 | admin/manager | 직원 정보 접근 요약 |
| GET  | `/api/audit/access-summary/contract/<int:contract_id>` | 필수 | admin/manager | 계약 정보 접근 요약 |

#### 10.3 메타 정보

| HTTP | 엔드포인트 | 인증 | 역할 | 설명 |
|------|-----------|------|------|------|
| GET  | `/api/audit/actions` | 필수 | - | 액션 유형 목록 |
| GET  | `/api/audit/resource-types` | 필수 | - | 리소스 유형 목록 |

**액션 유형**:
- `view`: 조회
- `create`: 생성
- `update`: 수정
- `delete`: 삭제
- `export`: 내보내기
- `sync`: 동기화
- `login`: 로그인
- `logout`: 로그아웃
- `access_denied`: 접근 거부

**리소스 유형**:
- `employee`: 직원
- `contract`: 계약
- `personal_profile`: 개인 프로필
- `sync`: 동기화
- `snapshot`: 스냅샷
- `termination`: 퇴사 처리
- `user`: 사용자
- `company`: 법인
- `organization`: 조직

#### 10.4 감사 대시보드

| HTTP | 엔드포인트 | 인증 | 역할 | 설명 |
|------|-----------|------|------|------|
| GET  | `/admin/audit` | 필수 | admin | 감사 대시보드 페이지 |

---

## 11. 동기화

### Blueprint: `sync_bp` (prefix: `/api/sync`)

#### 11.1 동기화 실행

| HTTP | 엔드포인트 | 인증 | 역할 | 설명 |
|------|-----------|------|------|------|
| GET  | `/api/sync/fields/<int:contract_id>` | 필수 | - | 동기화 가능 필드 목록 |
| POST | `/api/sync/personal-to-employee/<int:contract_id>` | 필수 | personal | 개인→법인 동기화 (수동) |
| POST | `/api/sync/employee-to-personal/<int:contract_id>` | 필수 | corporate | 법인→개인 동기화 (역방향) |
| POST | `/api/sync/all-contracts` | 필수 | personal | 내 모든 활성 계약 동기화 |

**Request 예시** (POST `/api/sync/personal-to-employee/<int:contract_id>`):
```json
{
  "fields": ["name", "email", "phone"]
}
```

**Response 예시**:
```json
{
  "success": true,
  "synced_fields": ["name", "email", "phone"],
  "changes": [
    {"field": "name", "old_value": "홍길동", "new_value": "홍길동"},
    {"field": "email", "old_value": "old@example.com", "new_value": "new@example.com"}
  ],
  "logs": [1, 2, 3]
}
```

#### 11.2 스냅샷 (1회성 제공)

| HTTP | 엔드포인트 | 인증 | 역할 | 설명 |
|------|-----------|------|------|------|
| GET  | `/api/sync/snapshot/<int:contract_id>` | 필수 | - | 1회성 스냅샷 조회 |
| POST | `/api/sync/snapshot/<int:contract_id>/apply` | 필수 | corporate | 스냅샷 적용 |

**Query Parameters** (`/api/sync/snapshot/<int:contract_id>`):
- `include_relations`: 관계 데이터 포함 여부 (true/false, 기본 true)

#### 11.3 계약 목록 및 설정

| HTTP | 엔드포인트 | 인증 | 역할 | 설명 |
|------|-----------|------|------|------|
| GET  | `/api/sync/contracts` | 필수 | personal | 내 활성 계약 목록 조회 |
| PUT  | `/api/sync/settings/<int:contract_id>/realtime` | 필수 | personal | 실시간 동기화 설정 변경 |

**Request 예시** (PUT `/api/sync/settings/<int:contract_id>/realtime`):
```json
{
  "enabled": true
}
```

#### 11.4 퇴사/종료 처리

| HTTP | 엔드포인트 | 인증 | 역할 | 설명 |
|------|-----------|------|------|------|
| POST | `/api/sync/terminate/<int:contract_id>` | 필수 | - | 계약 종료 처리 |
| GET  | `/api/sync/retention/<int:contract_id>` | 필수 | - | 데이터 보관 상태 조회 |
| GET  | `/api/sync/termination-history` | 필수 | - | 종료된 계약 이력 조회 |

#### 11.5 동기화 로그

| HTTP | 엔드포인트 | 인증 | 역할 | 설명 |
|------|-----------|------|------|------|
| GET  | `/api/sync/logs/<int:contract_id>` | 필수 | - | 동기화 로그 조회 |
| GET  | `/api/sync/field-mappings` | 필수 | - | 필드 매핑 정보 조회 (개발용) |

---

## 12. 계정 설정

### Blueprint: `account_bp` (prefix: `/account`)

| HTTP | 엔드포인트 | 인증 | 역할 | 설명 |
|------|-----------|------|------|------|
| GET  | `/account/settings` | 필수 | - | 계정 설정 메인 페이지 |
| GET  | `/account/password` | 필수 | - | 비밀번호 변경 페이지 |
| POST | `/account/password` | 필수 | - | 비밀번호 변경 처리 |
| GET  | `/account/privacy` | 필수 | - | 개인정보 공개 설정 페이지 |
| POST | `/account/privacy` | 필수 | - | 개인정보 공개 설정 저장 |
| GET  | `/account/delete` | 필수 | - | 계정 탈퇴 페이지 |
| POST | `/account/delete` | 필수 | - | 계정 탈퇴 처리 |

**Request 예시** (POST `/account/privacy`):
```form-data
show_email: "on"
show_phone: "on"
show_address: "on"
show_birth_date: "on"
show_profile_photo: "on"
```

---

## 13. 첨부파일 관리

### Blueprint: `attachment_bp` (prefix: `/api/attachments`)

> **도메인**: `app/domains/attachment/` (2026-01-10 신규)

#### 13.1 첨부파일 CRUD

| HTTP | 엔드포인트 | 인증 | 역할 | 설명 |
|------|-----------|------|------|------|
| POST | `/api/attachments` | 필수 | - | 파일 업로드 |
| DELETE | `/api/attachments/<int:id>` | 필수 | - | 파일 삭제 |
| GET | `/api/attachments/<owner_type>/<int:owner_id>` | 필수 | - | 파일 목록 조회 |

**Request 예시** (POST `/api/attachments`):
```form-data
file: [binary]
owner_type: "employee"
owner_id: 1
category: "document"
```

**Response 예시**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "file_name": "resume.pdf",
    "file_path": "/uploads/attachments/2026/01/resume.pdf",
    "file_type": "application/pdf",
    "file_size": 102400,
    "owner_type": "employee",
    "owner_id": 1,
    "category": "document",
    "upload_date": "2026-01-10"
  }
}
```

**owner_type 값**:
- `employee`: 직원 첨부파일
- `profile`: 개인 프로필 첨부파일
- `contract`: 계약 첨부파일

**category 값**:
- `document`: 문서
- `photo`: 사진
- `businesscard`: 명함
- `certificate`: 증빙 서류

---

## 14. 명함 관리

### Blueprint: `businesscard_bp` (prefix: `/api/businesscard`)

> **도메인**: `app/domains/businesscard/` (2026-01-09 신규)

#### 14.1 명함 CRUD

| HTTP | 엔드포인트 | 인증 | 역할 | 설명 |
|------|-----------|------|------|------|
| POST | `/api/businesscard/employee/<int:employee_id>` | 필수 | corporate | 명함 업로드 |
| DELETE | `/api/businesscard/employee/<int:employee_id>/<side>` | 필수 | corporate | 명함 삭제 |
| GET | `/api/businesscard/employee/<int:employee_id>` | 필수 | - | 명함 조회 |

**Request 예시** (POST `/api/businesscard/employee/<int:employee_id>`):
```form-data
file: [binary]
side: "front"  # front 또는 back
```

**Response 예시**:
```json
{
  "success": true,
  "data": {
    "front": {
      "id": 1,
      "file_path": "/uploads/businesscards/emp_1_front.jpg",
      "upload_date": "2026-01-09"
    },
    "back": {
      "id": 2,
      "file_path": "/uploads/businesscards/emp_1_back.jpg",
      "upload_date": "2026-01-09"
    }
  }
}
```

**side 값**:
- `front`: 명함 앞면
- `back`: 명함 뒷면

---

## 15. 기타

### Blueprint: `main_bp` (no prefix)

| HTTP | 엔드포인트 | 인증 | 역할 | 설명 |
|------|-----------|------|------|------|
| GET  | `/` | - | - | 메인 페이지/대시보드 |
| GET  | `/search` | 필수 | - | 직원 검색 |
| GET  | `/examples/data-table` | 필수 | - | 데이터 테이블 데모 페이지 |
| GET  | `/examples/styleguide` | 필수 | - | 스타일 가이드 페이지 |

### Blueprint: `mypage_bp` (prefix: `/my`)

| HTTP | 엔드포인트 | 인증 | 역할 | 설명 |
|------|-----------|------|------|------|
| GET  | `/my/company` | 필수 | employee | 회사 인사카드 (직원용) |

---

## RESTful API 규칙 준수 여부 분석

### 준수 사항
1. **리소스 기반 URL**: `/employees`, `/contracts`, `/organizations` 등 명사형 리소스 사용
2. **HTTP 메서드 활용**: GET(조회), POST(생성), PUT(수정), DELETE(삭제) 적절히 사용
3. **계층 구조**: `/employees/<id>`, `/contracts/<id>` 등 계층 구조 표현
4. **JSON 응답**: API는 대부분 JSON 형식으로 응답

### 개선 권장 사항
1. **URL 일관성**:
   - `/api/` prefix 불일치 (일부 API만 prefix 사용)
   - 권장: 모든 REST API는 `/api/` prefix 사용

2. **HTTP 메서드 혼용**:
   - `POST /employees/<id>/update` → `PUT /employees/<id>` 권장
   - `POST /employees/<id>/delete` → `DELETE /employees/<id>` 권장

3. **응답 형식 표준화**:
   - 성공: `{"success": true, "data": {...}}`
   - 실패: `{"success": false, "error": "message"}`
   - 일부 엔드포인트에서 `message` 필드 혼재

4. **페이지네이션**:
   - 일부 API만 `limit`, `offset` 지원
   - 권장: 모든 목록 조회 API에 페이지네이션 적용

5. **버전 관리**:
   - 현재 버전 정보 없음
   - 권장: `/api/v1/` 등 버전 관리 도입

---

## 인증 및 권한 매트릭스

| 엔드포인트 그룹 | 인증 필요 | 역할 제한 | 특이사항 |
|----------------|----------|----------|---------|
| 인증 (`/auth/*`) | - | - | 로그인 전 접근 가능 |
| 직원 목록 (`/employees`) | 필수 | manager/admin | employee는 본인만 |
| 직원 상세 (`/employees/<id>`) | 필수 | - | employee는 본인만 |
| 직원 생성/수정 (`/employees`) | 필수 | manager/admin | - |
| 직원 삭제 | 필수 | admin | - |
| 계약 목록 | 필수 | 계정 타입별 | personal/employee_sub/corporate |
| 계약 승인/거절 | 필수 | 당사자 | - |
| 법인 회원가입 | - | - | - |
| 법인 대시보드 | 필수 | corporate | - |
| 법인 사용자 관리 | 필수 | admin | - |
| 개인 회원가입 | - | - | - |
| 개인 대시보드 | 필수 | personal | - |
| 프로필 조회/수정 | 필수 | - | 본인만 |
| 분류 옵션 조회 | 필수 | - | - |
| 분류 옵션 수정 | 필수 | admin | - |
| 조직 조회 | 필수 | - | 멀티테넌시 적용 |
| 조직 관리 | 필수 | admin | 멀티테넌시 적용 |
| 알림 조회 | 필수 | - | 본인만 |
| 감사 로그 조회 | 필수 | admin/manager | 본인 로그는 일반 사용자도 |
| 동기화 실행 | 필수 | 계정 타입별 | personal/corporate |

---

## 응답 코드 규칙

### 성공 응답
- `200 OK`: 조회, 수정 성공
- `201 Created`: 생성 성공
- `301 Moved Permanently`: 리다이렉트 (영구 이동)

### 클라이언트 오류
- `400 Bad Request`: 잘못된 요청 데이터
- `401 Unauthorized`: 인증 필요
- `403 Forbidden`: 권한 없음
- `404 Not Found`: 리소스 없음

### 서버 오류
- `500 Internal Server Error`: 서버 내부 오류

---

## 문서 버전

- **Version**: 1.1
- **Last Updated**: 2026-01-11
- **Contributors**: Backend Architect (AI)

### 변경 이력
| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| 1.1 | 2026-01-11 | 첨부파일/명함 API 추가 |
| 1.0 | 2025-12-16 | 초기 문서 작성 |
