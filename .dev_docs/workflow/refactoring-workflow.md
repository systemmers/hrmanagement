# JS/Python 기능 분리 리팩토링 워크플로우

## 개요
- 목표: SoC/SRP 준수율 향상 (Python 65% → 80%)
- 전략: 안전한 단계별 리팩토링 (--safe 모드)
- 예상 기간: Phase별 순차 진행

---

## Phase 1: HIGH 우선순위 (즉시)

### Task 1.1: ContractService 생성 및 contracts.py 리팩토링

**목표**: Routes → Service → Repository 계층 분리

**체크리스트**:
- [ ] `app/services/contract_service.py` 신규 생성
- [ ] person_contract_repo 호출 로직을 Service로 이전
- [ ] contracts.py에서 Service import 및 호출로 변경
- [ ] 기존 기능 테스트 (계약 생성/승인/거절/종료)
- [ ] 멀티테넌시 검증

**의존성**:
```
contracts.py
├── person_contract_repo → ContractService로 이전
├── user_repo → 유지
└── contract_helpers → 유지
```

**안전 검증**:
- [ ] 기존 API 엔드포인트 동작 확인
- [ ] 세션/인증 처리 정상 동작
- [ ] 에러 핸들링 유지

---

### Task 1.2: employees/helpers.py 분할

**목표**: 단일 책임 원칙에 따른 모듈 분리

**분할 계획**:
```
helpers.py (441 lines)
├── form_extractors.py (~150 lines)
│   ├── extract_employee_from_form()
│   ├── extract_basic_fields_from_form()
│   └── 관련 헬퍼 함수
├── file_handlers.py (~100 lines)
│   ├── allowed_image_file()
│   ├── get_file_extension()
│   ├── get_profile_photo_folder()
│   ├── get_business_card_folder()
│   ├── generate_unique_filename()
│   └── MAX_IMAGE_SIZE 상수
└── relation_updaters.py (~190 lines)
    ├── RelatedDataUpdater 클래스
    ├── update_family_data()
    ├── update_education_data()
    ├── update_career_data()
    ├── update_certificate_data()
    ├── update_language_data()
    ├── update_military_data()
    ├── update_project_data()
    └── update_award_data()
```

**체크리스트**:
- [ ] form_extractors.py 생성 및 함수 이동
- [ ] file_handlers.py 생성 및 함수 이동
- [ ] relation_updaters.py 생성 및 함수 이동
- [ ] helpers.py를 __init__.py로 변환 (re-export)
- [ ] routes.py import 경로 업데이트
- [ ] 기능 테스트 (직원 생성/수정/삭제)

**안전 검증**:
- [ ] 모든 import 경로 정상 동작
- [ ] 하위 호환성 유지 (기존 import 문 동작)
- [ ] 파일 업로드 기능 정상

---

### Task 1.3: employees/routes.py 분할

**목표**: 라우트 책임별 모듈 분리

**분할 계획**:
```
routes.py (542 lines)
├── list_routes.py (~180 lines)
│   ├── employee_list() - GET /employees
│   ├── employee_search() - GET /employees/search
│   └── 필터/정렬 로직
├── detail_routes.py (~200 lines)
│   ├── employee_detail() - GET /employees/<id>
│   ├── employee_create() - POST /employees
│   ├── employee_update() - PUT /employees/<id>
│   └── employee_delete() - DELETE /employees/<id>
└── relation_routes.py (~160 lines)
    ├── employee_family() - /employees/<id>/family
    ├── employee_education() - /employees/<id>/education
    └── 기타 관계 데이터 라우트
```

**체크리스트**:
- [ ] list_routes.py 생성 및 라우트 이동
- [ ] detail_routes.py 생성 및 라우트 이동
- [ ] relation_routes.py 생성 및 라우트 이동
- [ ] Blueprint 통합 (routes/__init__.py)
- [ ] URL 라우팅 테스트
- [ ] 기능 테스트 (CRUD 전체)

**안전 검증**:
- [ ] 모든 URL 경로 정상 동작
- [ ] 인증/권한 데코레이터 유지
- [ ] 템플릿 렌더링 정상

---

## Phase 2: MEDIUM 우선순위 (중기)

### Task 2.1: employee_service.py 분할

**분할 계획**:
```
employee_service.py (515 lines)
├── employee_crud_service.py (~250 lines)
│   ├── get_employee()
│   ├── get_employees_by_org()
│   ├── create_employee()
│   ├── update_employee()
│   └── delete_employee()
└── employee_relation_service.py (~265 lines)
    ├── update_education()
    ├── update_career()
    ├── update_family()
    └── 기타 관계 데이터 메서드
```

**체크리스트**:
- [ ] employee_crud_service.py 생성
- [ ] employee_relation_service.py 생성
- [ ] 기존 import 경로 업데이트
- [ ] 통합 테스트

---

### Task 2.2: notification_service.py 분할

**분할 계획**:
```
notification_service.py (505 lines)
├── notification_service.py (~300 lines)
│   ├── 알림 생성/조회/삭제
│   └── 알림 전송 로직
└── preference_service.py (~205 lines)
    ├── 사용자 알림 설정
    └── 구독/해제 로직
```

**체크리스트**:
- [ ] preference_service.py 분리
- [ ] notification_service.py 정리
- [ ] 기존 import 경로 업데이트
- [ ] 알림 기능 테스트

---

### Task 2.3: contract-api.js 이동 (Frontend)

**이동 계획**:
```
변경 전: app/static/js/utils/contract-api.js
변경 후: app/static/js/services/contract-service.js
```

**체크리스트**:
- [ ] services/contract-service.js로 파일 이동
- [ ] import 경로 수정 (./api.js → ../utils/api.js)
- [ ] HTML 템플릿 스크립트 경로 업데이트
- [ ] window.HRContractAPI 전역 노출 유지
- [ ] 계약 승인/거절/종료 기능 테스트

**영향 파일**:
- [ ] app/templates/contracts/detail.html (스크립트 경로)
- [ ] 기타 계약 관련 템플릿

---

## Phase 3: LOW 우선순위 (장기)

### Task 3.1: models/domains/ 구조 활성화

**체크리스트**:
- [ ] domains/__init__.py 파일 활성화
- [ ] 도메인별 모델 import 정리
- [ ] 기존 import 경로 호환성 유지

---

## 품질 검증 체크리스트

### 기능 테스트
- [ ] 직원 CRUD (생성/조회/수정/삭제)
- [ ] 계약 관리 (생성/승인/거절/종료)
- [ ] 파일 업로드 (프로필 사진/명함)
- [ ] 관계 데이터 (가족/학력/경력 등)
- [ ] 알림 기능

### 비기능 테스트
- [ ] 멀티테넌시 격리
- [ ] 인증/권한 처리
- [ ] 에러 핸들링
- [ ] 성능 (응답 시간)

### 코드 품질
- [ ] 500라인 초과 파일 수: 14개 → 5개 이하
- [ ] SRP 준수율: 65% → 80%
- [ ] SoC 준수율: 70% → 85%
- [ ] Service 레이어 활용: 70% → 90%

---

## 롤백 계획

각 Phase 완료 후 문제 발생 시:
1. Git 커밋으로 이전 상태 복원 가능
2. 분할된 파일을 원본으로 병합
3. import 경로 원복

**안전 원칙**:
- 각 Task 완료 후 커밋
- 테스트 통과 후 다음 Task 진행
- 문제 발생 시 즉시 롤백

---

## 진행 상태

| Phase | Task | 상태 | 완료일 |
|-------|------|------|--------|
| 1 | ContractService 생성 | 대기 | - |
| 1 | helpers.py 분할 | 대기 | - |
| 1 | routes.py 분할 | 대기 | - |
| 2 | employee_service.py 분할 | 대기 | - |
| 2 | notification_service.py 분할 | 대기 | - |
| 2 | contract-api.js 이동 | 대기 | - |
| 3 | domains/ 구조 활성화 | 대기 | - |
