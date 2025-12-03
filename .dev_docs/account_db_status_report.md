# 계정 DB 현황 보고서

생성일: 2025-12-03

---

## 1. 전체 통계

| 항목 | 수량 |
|------|------|
| 총 사용자(User) 수 | 19명 |
| 총 법인(Company) 수 | 3개 |
| 총 직원(Employee) 수 | 10명 |

---

## 2. 계정 유형별 분포

| 계정 유형 (account_type) | 수량 | 설명 |
|--------------------------|------|------|
| personal | 5명 | 독립 개인 계정 |
| corporate | 6명 | 법인 관리자 계정 |
| employee_sub | 8명 | 법인소속 직원 하위계정 |

---

## 3. Role별 분포

| Role | 수량 | 권한 |
|------|------|------|
| admin | 5명 | 전체 관리 권한 |
| manager | 0명 | 직원 관리 권한 |
| employee | 14명 | 본인 정보 열람 |

---

## 4. 법인별 상세 현황

### 4.1 테스트기업(주) (Company ID: 1)

| 항목 | 값 |
|------|-----|
| 사업자번호 | 1234567890 |
| root_organization_id | 2 |
| 법인 관리자 계정 | 4명 |
| 직원 하위 계정 | 5명 |
| Employee 레코드 | 10명 |

**관리자 계정:**
| ID | Username | Role |
|----|----------|------|
| 2 | company@example.com | admin |
| 3 | testadmin | admin |
| 10 | corp_admin_a | admin |
| 1 | testuser@example.com | employee |

**직원 하위 계정:**
| ID | Username | Employee 연결 |
|----|----------|---------------|
| 12 | emp_a1 | X |
| 13 | emp_a2 | X |
| 14 | emp_a3 | X |
| 15 | emp_a4 | X |
| 16 | emp_a5 | X |

---

### 4.2 (주)테스트기업 (Company ID: 2)

| 항목 | 값 |
|------|-----|
| 사업자번호 | 9998877777 |
| root_organization_id | 3 |
| 법인 관리자 계정 | 1명 |
| 직원 하위 계정 | 0명 |
| Employee 레코드 | 0명 |

**관리자 계정:**
| ID | Username | Role |
|----|----------|------|
| 6 | newcorp_admin | admin |

---

### 4.3 테스트기업 B (Company ID: 3)

| 항목 | 값 |
|------|-----|
| 사업자번호 | 0987654321 |
| root_organization_id | 4 |
| 법인 관리자 계정 | 1명 |
| 직원 하위 계정 | 3명 |
| Employee 레코드 | 0명 |

**관리자 계정:**
| ID | Username | Role |
|----|----------|------|
| 11 | corp_admin_b | admin |

**직원 하위 계정:**
| ID | Username | Employee 연결 |
|----|----------|---------------|
| 17 | emp_b1 | X |
| 18 | emp_b2 | X |
| 19 | emp_b3 | X |

---

## 5. 개인(Personal) 계정 목록

| ID | Username | Email |
|----|----------|-------|
| 4 | personaltest | personal@example.com |
| 5 | newpersonal | newpersonal@example.com |
| 7 | personal_user1 | personal1@test.com |
| 8 | personal_user2 | personal2@test.com |
| 9 | personal_user3 | personal3@test.com |

---

## 6. Employee-User 연결 현황

| 상태 | 수량 | 비고 |
|------|------|------|
| Employee 연결됨 | 1명 | testuser@example.com (ID:1) |
| Employee 미연결 | 13명 | 법인/직원 계정 중 미연결 |

**연결된 계정:**
- User ID: 1 (testuser@example.com) -> Employee ID: 1 (김철수)

---

## 7. Employee Organization 분포

| organization_id | 직원 수 | 소속 법인 |
|-----------------|---------|----------|
| 2 | 10명 | 테스트기업(주) |
| 3 | 0명 | (주)테스트기업 |
| 4 | 0명 | 테스트기업 B |

---

## 8. 테스트 계정 정보

### 8.1 개인 계정
| Username | Password | 용도 |
|----------|----------|------|
| personal_user1 | personal1234 | 개인 계정 테스트 |
| personal_user2 | personal1234 | 개인 계정 테스트 |
| personal_user3 | personal1234 | 개인 계정 테스트 |

### 8.2 법인 관리자 계정
| Username | Password | 소속 | 용도 |
|----------|----------|------|------|
| company@example.com | admin1234 | 테스트기업(주) | 기본 관리자 |
| corp_admin_a | corp1234 | 테스트기업(주) | 멀티테넌시 테스트 |
| corp_admin_b | corp1234 | 테스트기업 B | 멀티테넌시 테스트 |

### 8.3 직원 연결된 계정
| Username | Password | Employee | 용도 |
|----------|----------|----------|------|
| testuser@example.com | test1234 | 김철수 (ID:1) | 직원 인사카드 접근 |

### 8.4 직원 하위 계정 (Employee 미연결)
| Username | Password | 소속 | 상태 |
|----------|----------|------|------|
| emp_a1~a5 | emp1234 | 테스트기업(주) | 로그인 시 로그아웃 처리 |
| emp_b1~b3 | emp1234 | 테스트기업 B | 로그인 시 로그아웃 처리 |

---

## 9. 주요 발견사항 및 권장사항

### 9.1 발견된 이슈

| 이슈 | 심각도 | 설명 |
|------|--------|------|
| Employee-User 미연결 | Medium | employee_sub 계정 8명이 Employee와 연결되지 않아 로그인 후 로그아웃 처리됨 |
| 법인별 Employee 불균형 | Low | 테스트기업(주)에만 10명의 Employee 존재, 다른 법인은 0명 |
| Manager Role 부재 | Low | manager 권한 사용자가 0명 |

### 9.2 권장사항

1. **Employee-User 연결 필요**
   - employee_sub 계정 생성 시 Employee 레코드 자동 생성 로직 추가 권장
   - 기존 미연결 계정에 대한 Employee 생성 스크립트 작성

2. **테스트 데이터 보완**
   - 테스트기업 B, (주)테스트기업에 Employee 샘플 데이터 추가
   - Manager Role 테스트를 위한 계정 생성

3. **멀티테넌시 검증 완료**
   - 모든 법인의 root_organization_id 정상 설정 확인
   - Employee.organization_id 기반 데이터 격리 정상 작동

---

## 10. 데이터 모델 관계도

```
User (사용자)
├── account_type: personal | corporate | employee_sub
├── company_id → Company.id (법인 소속)
├── employee_id → Employee.id (직원 연결)
└── role: admin | manager | employee

Company (법인)
├── root_organization_id → Organization.id (조직 루트)
└── business_number (사업자번호)

Employee (직원)
├── organization_id → Organization.id (소속 조직)
└── 인사 정보 (이름, 부서, 직급 등)

Organization (조직)
├── id (조직 ID)
├── name (조직명)
└── parent_id → Organization.id (상위 조직)
```

---

## 변경 이력

| 날짜 | 작성자 | 내용 |
|------|--------|------|
| 2025-12-03 | Claude | 최초 작성 |
