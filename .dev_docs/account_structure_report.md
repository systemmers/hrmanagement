# 계정 구조 분석 보고서

분석일: 2025-12-03 (최종 업데이트)

## 1. 멀티테넌시 구조 개요

```
플랫폼 계정 구조
├── personal (개인계정)
│   └── 독립적인 개인 사용자
│       - 프로필 관리
│       - 법인과 계약 체결 가능
│
├── corporate (법인계정)
│   └── 기업 관리자
│       - 직원 관리
│       - 조직 관리
│       - 계약 관리
│       └── employee_sub (법인소속 직원계정)
│           - 법인이 생성/관리하는 하위 계정
│           - parent_user_id로 법인관리자와 연결
│           - Employee 레코드 연결 필수
```

---

## 2. 현재 데이터베이스 상태

### 2.1 전체 현황

| 항목 | 수량 |
|------|------|
| 전체 사용자 | 19명 |
| 법인(Company) | 3개 |
| 직원(Employee) | 28명 |

### 2.2 계정 유형별 분포

| 계정 유형 | 수량 | 설명 |
|-----------|------|------|
| personal | 5명 | 개인 계정 |
| corporate | 6명 | 법인 관리자 계정 |
| employee_sub | 8명 | 법인소속 직원 계정 |

---

## 3. 법인별 상세

### 3.1 테스트기업(주) (ID: 1)

| 항목 | 값 |
|------|-----|
| 사업자번호 | 123-45-67890 |
| root_organization_id | 2 |
| 법인계정 | 4명 |
| 직원계정 | 5명 |
| Employee 레코드 | 15명 |

**법인 관리자:**
| ID | Username | Email | Role |
|----|----------|-------|------|
| 2 | company@example.com | company@example.com | admin |
| 3 | testadmin | testadmin@testcompany.com | admin |
| 10 | corp_admin_a | corp_a@test.com | admin |
| 1 | testuser@example.com | testuser@example.com | employee |

**소속 직원계정:**
| ID | Username | Parent | Employee 연결 |
|----|----------|--------|---------------|
| 12 | emp_a1 | corp_admin_a | 이미영 (ID: 28) |
| 13 | emp_a2 | corp_admin_a | 최하늘 (ID: 21) |
| 14 | emp_a3 | corp_admin_a | 박민호 (ID: 22) |
| 15 | emp_a4 | corp_admin_a | 주세영 (ID: 23) |
| 16 | emp_a5 | corp_admin_a | 윤정민 (ID: 24) |

### 3.2 (주)테스트기업 (ID: 2)

| 항목 | 값 |
|------|-----|
| 사업자번호 | 999-88-77777 |
| root_organization_id | 3 |
| 법인계정 | 1명 |
| 직원계정 | 0명 |
| Employee 레코드 | 5명 |

**법인 관리자:**
| ID | Username | Email | Role |
|----|----------|-------|------|
| 6 | newcorp_admin | newcorp@example.com | admin |

### 3.3 테스트기업 B (ID: 3)

| 항목 | 값 |
|------|-----|
| 사업자번호 | 098-76-54321 |
| root_organization_id | 4 |
| 법인계정 | 1명 |
| 직원계정 | 3명 |
| Employee 레코드 | 8명 |

**법인 관리자:**
| ID | Username | Email | Role |
|----|----------|-------|------|
| 11 | corp_admin_b | corp_b@test.com | admin |

**소속 직원계정:**
| ID | Username | Parent | Employee 연결 |
|----|----------|--------|---------------|
| 17 | emp_b1 | corp_admin_b | 장유진 (ID: 25) |
| 18 | emp_b2 | corp_admin_b | 한서연 (ID: 26) |
| 19 | emp_b3 | corp_admin_b | 최도현 (ID: 27) |

---

## 4. 개인계정 목록

| ID | Username | Email |
|----|----------|-------|
| 4 | personaltest | personal@example.com |
| 5 | newpersonal | newpersonal@example.com |
| 7 | personal_user1 | personal1@test.com |
| 8 | personal_user2 | personal2@test.com |
| 9 | personal_user3 | personal3@test.com |

---

## 5. 로그인 동작 분석

### 5.1 계정 유형별 리다이렉트 로직

| 계정 유형 | Role | Employee 연결 | 리다이렉트 |
|-----------|------|---------------|------------|
| personal | * | * | /personal/dashboard |
| corporate | admin | * | / (메인 대시보드) |
| corporate | employee | 연결됨 | /employees/{id} |
| corporate | employee | 미연결 | 로그아웃 |
| employee_sub | employee | 연결됨 | /employees/{id} |
| employee_sub | employee | 미연결 | 로그아웃 |

### 5.2 E2E 테스트 결과 (2025-12-03 검증 완료)

| 계정 | 유형 | 로그인 | 리다이렉트 | 상태 |
|------|------|--------|------------|------|
| personal_user1 | personal | PASS | /personal/profile/edit | 정상 |
| corp_admin_a | corporate/admin | PASS | / | 정상 |
| corp_admin_b | corporate/admin | PASS | / (8명 표시) | 정상 |
| testuser@example.com | corporate/employee | PASS | /employees/1 | 정상 |
| emp_a1 | employee_sub | PASS | /employees/28 (이미영) | 정상 |
| emp_b1 | employee_sub | PASS | /employees/25 (장유진) | 정상 |

---

## 6. 테스트 계정 요약

### 6.1 개인계정
| Username | Password | 비고 |
|----------|----------|------|
| personal_user1 | personal1234 | 테스트용 |
| personal_user2 | personal1234 | 테스트용 |
| personal_user3 | personal1234 | 테스트용 |
| personaltest | (확인필요) | 초기 테스트 |
| newpersonal | (확인필요) | 초기 테스트 |

### 6.2 법인계정 (관리자)
| Username | Password | 법인 | 비고 |
|----------|----------|------|------|
| company@example.com | admin1234 | 테스트기업(주) | 기본 관리자 |
| testadmin | (확인필요) | 테스트기업(주) | 초기 테스트 |
| corp_admin_a | corp1234 | 테스트기업(주) | 멀티테넌시 테스트 |
| newcorp_admin | (확인필요) | (주)테스트기업 | 초기 테스트 |
| corp_admin_b | corp1234 | 테스트기업 B | 멀티테넌시 테스트 |

### 6.3 법인소속 직원계정 (Employee 연결됨)
| Username | Password | 법인 | Employee |
|----------|----------|------|----------|
| testuser@example.com | test1234 | 테스트기업(주) | 김철수 (ID: 1) |
| emp_a1 | emp1234 | 테스트기업(주) | 이미영 (ID: 28) |
| emp_a2 | emp1234 | 테스트기업(주) | 최하늘 (ID: 21) |
| emp_a3 | emp1234 | 테스트기업(주) | 박민호 (ID: 22) |
| emp_a4 | emp1234 | 테스트기업(주) | 주세영 (ID: 23) |
| emp_a5 | emp1234 | 테스트기업(주) | 윤정민 (ID: 24) |
| emp_b1 | emp1234 | 테스트기업 B | 장유진 (ID: 25) |
| emp_b2 | emp1234 | 테스트기업 B | 한서연 (ID: 26) |
| emp_b3 | emp1234 | 테스트기업 B | 최도현 (ID: 27) |

---

## 7. 데이터 모델 관계도

```
User (사용자)
├── account_type: personal | corporate | employee_sub
├── company_id → Company.id (법인 소속)
├── employee_id → Employee.id (직원 연결)
├── parent_user_id → User.id (상위 관리자, employee_sub용)
└── role: admin | manager | employee

Company (법인)
├── id (법인 ID)
├── name (법인명)
├── business_number (사업자번호)
└── root_organization_id → Organization.id (조직 루트)

Organization (조직)
├── id (조직 ID)
├── name (조직명)
├── company_id → Company.id
└── parent_id → Organization.id (상위 조직)

Employee (직원)
├── id (직원 ID)
├── name (이름)
├── employee_number (사번)
├── organization_id → Organization.id (소속 조직)
└── 인사 정보 (부서, 직급, 급여 등)
```

---

## 8. 변경 이력

| 날짜 | 내용 |
|------|------|
| 2025-12-03 | 최초 작성 |
| 2025-12-03 | 데이터 균형화 후 업데이트 - Employee 28명, 모든 employee_sub 연결 완료 |

---

## 9. 참고 스크립트

### 9.1 데이터 균형화 스크립트
```bash
# 상태 확인
python scripts/setup_balanced_test_data.py --status

# 미리보기 (변경 없음)
python scripts/setup_balanced_test_data.py --dry-run

# 실행
python scripts/setup_balanced_test_data.py
```

### 9.2 관련 파일
| 파일 | 설명 |
|------|------|
| `scripts/balance_test_data.py` | 법인별 Employee 생성 |
| `scripts/link_employee_user.py` | employee_sub-Employee 연결 |
| `scripts/setup_balanced_test_data.py` | 통합 실행 스크립트 |
