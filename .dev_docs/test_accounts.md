# 멀티테넌시 테스트 계정 정보

생성일: 2025-12-03

## 계정 구조

```
플랫폼
├── 개인계정 (personal) - 독립적인 개인 사용자
├── 법인계정 (corporate) - 기업 관리자
│   └── 법인소속 직원계정 (employee_sub) - 법인이 생성한 하위 계정
```

---

## 1. 개인계정 (Personal)

| No | Username | Email | Password | ID |
|----|----------|-------|----------|-----|
| 1 | personal_user1 | personal1@test.com | personal1234 | 7 |
| 2 | personal_user2 | personal2@test.com | personal1234 | 8 |
| 3 | personal_user3 | personal3@test.com | personal1234 | 9 |

**특징:**
- 독립적인 개인 계정
- 법인과 계약 체결 가능
- 개인 정보 직접 관리

---

## 2. 법인계정 (Corporate)

### 법인 A: 테스트기업 A

| 항목 | 값 |
|------|-----|
| Company ID | 1 |
| 기업명 | 테스트기업 A |
| 사업자번호 | 123-45-67890 |
| 대표자 | 홍길동 |

**법인 관리자 계정:**

| Username | Email | Password | Role | ID |
|----------|-------|----------|------|-----|
| corp_admin_a | corp_a@test.com | corp1234 | admin | 10 |

---

### 법인 B: 테스트기업 B

| 항목 | 값 |
|------|-----|
| Company ID | 3 |
| 기업명 | 테스트기업 B |
| 사업자번호 | 098-76-54321 |
| 대표자 | 김철수 |

**법인 관리자 계정:**

| Username | Email | Password | Role | ID |
|----------|-------|----------|------|-----|
| corp_admin_b | corp_b@test.com | corp1234 | admin | 11 |

---

## 3. 법인소속 직원계정 (Employee Sub)

### 법인 A 소속 (5명)

| No | Username | Email | Password | Parent | ID |
|----|----------|-------|----------|--------|-----|
| 1 | emp_a1 | emp_a1@test.com | emp1234 | corp_admin_a | 12 |
| 2 | emp_a2 | emp_a2@test.com | emp1234 | corp_admin_a | 13 |
| 3 | emp_a3 | emp_a3@test.com | emp1234 | corp_admin_a | 14 |
| 4 | emp_a4 | emp_a4@test.com | emp1234 | corp_admin_a | 15 |
| 5 | emp_a5 | emp_a5@test.com | emp1234 | corp_admin_a | 16 |

### 법인 B 소속 (3명)

| No | Username | Email | Password | Parent | ID |
|----|----------|-------|----------|--------|-----|
| 1 | emp_b1 | emp_b1@test.com | emp1234 | corp_admin_b | 17 |
| 2 | emp_b2 | emp_b2@test.com | emp1234 | corp_admin_b | 18 |
| 3 | emp_b3 | emp_b3@test.com | emp1234 | corp_admin_b | 19 |

**특징:**
- 법인이 생성하고 관리하는 하위 계정
- parent_user_id로 법인 관리자와 연결
- company_id로 법인과 연결

---

## 계정 유형별 요약

| 계정 유형 | 설명 | 생성 수 |
|-----------|------|---------|
| personal | 개인 계정 | 3개 |
| corporate | 법인 관리자 계정 | 2개 |
| employee_sub | 법인소속 직원 계정 | 8개 (5+3) |

---

## 기존 테스트 계정 (참고)

| Email | Password | 계정유형 | 비고 |
|-------|----------|---------|------|
| testuser@example.com | test1234 | corporate | 일반 직원 |
| company@example.com | admin1234 | corporate | 관리자 |

---

## 테스트 시나리오

### 1. 개인계정 로그인
```
Email: personal1@test.com
Password: personal1234
```

### 2. 법인계정 로그인
```
Email: corp_a@test.com
Password: corp1234
```

### 3. 법인소속 직원계정 로그인
```
Email: emp_a1@test.com
Password: emp1234
```

---

## 데이터베이스 모델 구조

### User 모델 (account_type)
- `personal`: 개인 계정
- `corporate`: 법인 계정
- `employee_sub`: 법인 하위 직원 계정

### 관계
- User.company_id -> Company.id (법인 연결)
- User.parent_user_id -> User.id (하위 계정의 부모)
