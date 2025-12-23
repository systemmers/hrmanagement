# 테스트 계정 정보

**최종 업데이트**: 2025-12-20

## 계정 현황

| 계정 유형 | 수량 | 설명 |
|----------|------|------|
| personal | 10 | 개인 계정 |
| corporate | 5 | 법인 관리자 계정 |
| employee_sub | 50 | 법인 소속 직원 계정 |
| **합계** | **65** | |

## 공통 비밀번호

모든 테스트 계정의 비밀번호: `test1234`

---

## 법인 목록

| ID | 법인명 | 직원수 | 관리자 이메일 |
|----|--------|--------|--------------|
| 1 | 테스트기업 A | 10 | admin@testcorp.co.kr |
| 2 | 테크솔루션즈 | 10 | admin@techsol.com |
| 3 | 글로벌코퍼레이션 | 10 | admin@globalcorp.co.kr |
| 4 | 스마트시스템즈 | 10 | admin@smartsys.net |
| 5 | 넥스트테크 | 10 | admin@nexttech.io |

---

## 개인계정 (personal)

개인 이력서 관리용 계정

| Email | 이름 | 비밀번호 |
|-------|------|----------|
| junhyuk.kim@gmail.com | 김준혁 | test1234 |
| seojun.lee@gmail.com | 이서준 | test1234 |
| doyun.park@gmail.com | 박도윤 | test1234 |
| siwoo.choi@gmail.com | 최시우 | test1234 |
| yejun.jung@gmail.com | 정예준 | test1234 |
| seoyun.kim@gmail.com | 김서윤 | test1234 |
| jiwoo.lee@gmail.com | 이지우 | test1234 |
| hayun.park@gmail.com | 박하윤 | test1234 |
| sua.choi@gmail.com | 최수아 | test1234 |
| minseo.jung@gmail.com | 정민서 | test1234 |

---

## 법인관리자 (corporate)

법인 인사관리 시스템 관리자 계정

| Email | 법인 | 역할 | 비밀번호 |
|-------|------|------|----------|
| admin@testcorp.co.kr | 테스트기업 A | admin | test1234 |
| admin@techsol.com | 테크솔루션즈 | admin | test1234 |
| admin@globalcorp.co.kr | 글로벌코퍼레이션 | admin | test1234 |
| admin@smartsys.net | 스마트시스템즈 | admin | test1234 |
| admin@nexttech.io | 넥스트테크 | admin | test1234 |

---

## 직원계정 (employee_sub)

법인 소속 직원 계정 (샘플)

### 테스트기업 A

| Email | 이름 | 비밀번호 |
|-------|------|----------|
| seo623@testcorp.co.kr | 서민재 | test1234 |
| shin49@testcorp.co.kr | 신예준 | test1234 |
| lee597@testcorp.co.kr | 이시우 | test1234 |
| kwon413@testcorp.co.kr | 권하윤 | test1234 |
| choi996@testcorp.co.kr | 최지아 | test1234 |
| jung330@testcorp.co.kr | 정지현 | test1234 |
| song653@testcorp.co.kr | 송예진 | test1234 |
| park697@testcorp.co.kr | 박지영 | test1234 |

### 테크솔루션즈

| Email | 이름 | 비밀번호 |
|-------|------|----------|
| choi687@techsol.com | 최재현 | test1234 |
| hong760@techsol.com | 홍재현 | test1234 |

---

## 테스트 시나리오

### 시나리오 1: 개인 프로필 관리
1. junhyuk.kim@gmail.com 로그인
2. 개인 프로필 조회/수정
3. 학력, 경력, 자격증 등 이력 관리

### 시나리오 2: 법인 직원 관리
1. admin@testcorp.co.kr 로그인
2. 직원 목록 조회
3. 직원 상세 정보 조회/수정
4. 계약, 급여, 조직 정보 관리

### 시나리오 3: 직원 본인 프로필
1. seo623@testcorp.co.kr 로그인
2. 본인 프로필 조회
3. 수정 가능 항목 확인

---

## URL 정보

| 환경 | URL |
|------|-----|
| 로컬 개발 | http://localhost:5200 |
| 로그인 | http://localhost:5200/login |
| 개인 대시보드 | http://localhost:5200/personal/dashboard |
| 법인 대시보드 | http://localhost:5200/employees |
