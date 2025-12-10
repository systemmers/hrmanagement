# 인터페이스 통합 구현 워크플로우

## 개요
- **프로젝트**: 법인/개인 계정 인터페이스 통합
- **기반 문서**: `interface_integration_design.md`
- **생성일**: 2025-12-10
- **전략**: Systematic (Phase 기반 단계적 구현)
- **모드**: Safe Mode (검증 게이트 포함)

---

## 워크플로우 구조

```
Phase 0 (CRITICAL)     Phase 1 (HIGH)         Phase 2 (HIGH)         Phase 3 (MEDIUM)      Phase 4 (LOW)
인프라 준비            템플릿 통합            라우트 통합            CSS/테마              검증/롤아웃
     │                     │                     │                     │                     │
     ▼                     ▼                     ▼                     ▼                     ▼
┌─────────┐          ┌─────────┐          ┌─────────┐          ┌─────────┐          ┌─────────┐
│Adapter  │    ──▶   │Main     │    ──▶   │Blueprint│    ──▶   │CSS Vars │    ──▶   │기능검증 │
│구현     │          │Template │          │등록     │          │적용     │          │         │
├─────────┤          ├─────────┤          ├─────────┤          ├─────────┤          ├─────────┤
│Decorator│          │Header   │          │Routes   │          │반응형   │          │UI검증   │
│구현     │          │Partial  │          │구현     │          │스타일   │          │         │
├─────────┤          ├─────────┤          ├─────────┤          ├─────────┤          ├─────────┤
│Context  │          │Nav      │          │Redirect │          │접근성   │          │보안검증 │
│Processor│          │Partial  │          │설정     │          │개선     │          │         │
├─────────┤          ├─────────┤          └─────────┘          └─────────┘          ├─────────┤
│Feature  │          │14 섹션  │                                                    │성능검증 │
│Flag     │          │Partials │                                                    │         │
└─────────┘          └─────────┘                                                    ├─────────┤
                                                                                    │롤아웃   │
                                                                                    └─────────┘
```

---

## Phase 0: 인프라 준비 (CRITICAL)

### 0.1 ProfileAdapter 구현
**파일**: `app/adapters/profile_adapter.py`

| 작업 ID | 작업 | 의존성 | 검증 |
|---------|------|--------|------|
| P0-01 | adapters 디렉토리 생성 | - | 디렉토리 존재 확인 |
| P0-02 | ProfileAdapter ABC 정의 | P0-01 | 추상 메서드 14개 정의 |
| P0-03 | EmployeeProfileAdapter 구현 | P0-02 | Employee 모델 연동 |
| P0-04 | PersonalProfileAdapter 구현 | P0-02 | PersonalProfile 모델 연동 |
| P0-05 | __init__.py 내보내기 설정 | P0-03, P0-04 | import 테스트 |

**검증 게이트**:
```bash
# 단위 테스트
python -c "from app.adapters import ProfileAdapter, EmployeeProfileAdapter, PersonalProfileAdapter; print('OK')"
```

### 0.2 통합 데코레이터 구현
**파일**: `app/blueprints/profile/decorators.py`

| 작업 ID | 작업 | 의존성 | 검증 |
|---------|------|--------|------|
| P0-06 | profile Blueprint 디렉토리 생성 | - | 디렉토리 존재 확인 |
| P0-07 | unified_profile_required 구현 | P0-05 | session 분기 로직 |
| P0-08 | corporate_only 구현 | P0-07 | 권한 검사 로직 |

**검증 게이트**:
```bash
# 데코레이터 import 테스트
python -c "from app.blueprints.profile.decorators import unified_profile_required; print('OK')"
```

### 0.3 Context Processor 구현
**파일**: `app/context_processors/profile_context.py`

| 작업 ID | 작업 | 의존성 | 검증 |
|---------|------|--------|------|
| P0-09 | context_processors 디렉토리 생성 | - | 디렉토리 존재 확인 |
| P0-10 | inject_profile_context 함수 구현 | P0-05 | 반환값 검증 |
| P0-11 | register_context_processors 구현 | P0-10 | 앱 등록 테스트 |

### 0.4 기능 플래그 설정
**파일**: `config.py`

| 작업 ID | 작업 | 의존성 | 검증 |
|---------|------|--------|------|
| P0-12 | ENABLE_UNIFIED_PROFILE 플래그 추가 | - | 환경변수 로드 |
| P0-13 | UNIFIED_PROFILE_ROLLOUT_PERCENT 추가 | P0-12 | 기본값 0 |

---

## Phase 1: 템플릿 통합 (HIGH)

### 1.1 템플릿 디렉토리 구조
```
app/templates/profile/
├── unified_profile.html
├── unified_profile_edit.html
└── partials/
    ├── _header_unified.html
    ├── _section_nav_unified.html
    └── sections/
        ├── _basic_info.html
        ├── _organization_info.html
        ├── _contract_info.html
        ├── _salary_info.html
        ├── _benefit_info.html
        ├── _insurance_info.html
        ├── _education_info.html
        ├── _career_info.html
        ├── _certificate_info.html
        ├── _language_info.html
        ├── _military_info.html
        ├── _employment_contract.html
        ├── _personnel_movement.html
        └── _attendance_assets.html
```

### 1.2 메인 템플릿 작업

| 작업 ID | 작업 | 의존성 | 검증 |
|---------|------|--------|------|
| P1-01 | profile 템플릿 디렉토리 생성 | P0 완료 | 구조 확인 |
| P1-02 | unified_profile.html 작성 | P1-01 | Jinja2 문법 검증 |
| P1-03 | _header_unified.html 작성 | P1-01 | 조건부 렌더링 검증 |
| P1-04 | _section_nav_unified.html 작성 | P1-01 | 섹션 링크 검증 |

### 1.3 섹션 Partials 작업

| 작업 ID | 작업 | 의존성 | 그룹 |
|---------|------|--------|------|
| P1-05 | _basic_info.html | P1-04 | 공통 |
| P1-06 | _organization_info.html | P1-04 | 법인 전용 |
| P1-07 | _contract_info.html | P1-04 | 법인 전용 |
| P1-08 | _salary_info.html | P1-04 | 법인 전용 |
| P1-09 | _benefit_info.html | P1-04 | 법인 전용 |
| P1-10 | _insurance_info.html | P1-04 | 법인 전용 |
| P1-11 | _education_info.html | P1-04 | 공통 |
| P1-12 | _career_info.html | P1-04 | 공통 |
| P1-13 | _certificate_info.html | P1-04 | 공통 |
| P1-14 | _language_info.html | P1-04 | 공통 |
| P1-15 | _military_info.html | P1-04 | 공통 |
| P1-16 | _employment_contract.html | P1-04 | 법인 전용 |
| P1-17 | _personnel_movement.html | P1-04 | 법인 전용 |
| P1-18 | _attendance_assets.html | P1-04 | 법인 전용 |

**병렬 실행 그룹**:
- 그룹 A (공통): P1-05, P1-11, P1-12, P1-13, P1-14, P1-15
- 그룹 B (법인): P1-06, P1-07, P1-08, P1-09, P1-10, P1-16, P1-17, P1-18

---

## Phase 2: 라우트 통합 (HIGH)

### 2.1 Blueprint 구현

| 작업 ID | 작업 | 의존성 | 검증 |
|---------|------|--------|------|
| P2-01 | profile/__init__.py 작성 | P1 완료 | Blueprint 등록 |
| P2-02 | profile/routes.py 작성 | P2-01 | 라우트 정의 |
| P2-03 | app.py Blueprint 등록 | P2-02 | 앱 시작 테스트 |

### 2.2 라우트 정의

| 라우트 | 메서드 | 설명 | 데코레이터 |
|--------|--------|------|------------|
| `/profile/` | GET | 프로필 조회 | @unified_profile_required |
| `/profile/edit` | GET | 프로필 수정 폼 | @unified_profile_required |
| `/profile/section/<name>` | GET | 섹션 API | @unified_profile_required |

### 2.3 리다이렉트 설정

| 작업 ID | 작업 | 기존 라우트 | 신규 라우트 |
|---------|------|-------------|-------------|
| P2-04 | 개인 프로필 리다이렉트 | /personal/profile | /profile/ |
| P2-05 | 법인 인사카드 리다이렉트 | /my/company | /profile/ |

---

## Phase 3: CSS/테마 통합 (MEDIUM)

### 3.1 CSS 작업

| 작업 ID | 작업 | 파일 | 검증 |
|---------|------|------|------|
| P3-01 | CSS 변수 정의 | profile.css | 테마 적용 확인 |
| P3-02 | 레이아웃 스타일 | profile.css | 반응형 테스트 |
| P3-03 | 컴포넌트 스타일 | profile.css | 브라우저 호환성 |
| P3-04 | 반응형 브레이크포인트 | profile.css | 640/768/1024px |

### 3.2 접근성 개선

| 작업 ID | 작업 | 항목 | 검증 |
|---------|------|------|------|
| P3-05 | aria-label 추가 | 네비게이션 | 스크린리더 테스트 |
| P3-06 | 키보드 네비게이션 | 전체 | Tab 순서 확인 |
| P3-07 | 색상 대비율 | 개인 테마 | 4.5:1 이상 |

---

## Phase 4: 검증 및 롤아웃 (LOW)

### 4.1 검증 체크리스트

**기능 검증**:
- [ ] 법인 직원 프로필 조회 정상 동작
- [ ] 일반 개인 프로필 조회 정상 동작
- [ ] 섹션 네비게이션 정상 동작
- [ ] 조건부 렌더링 정확성
- [ ] 데이터 로딩 성능

**UI/UX 검증**:
- [ ] 법인/개인 테마 색상 적용
- [ ] 반응형 레이아웃 (640px, 768px, 1024px)
- [ ] 접근성 (aria-label, 키보드 네비게이션)
- [ ] 로딩 상태 표시

**보안 검증**:
- [ ] 인증 데코레이터 동작
- [ ] 세션 관리 정상
- [ ] 권한 분리 (법인 전용 섹션)
- [ ] CSRF 토큰 검증

**성능 검증**:
- [ ] 템플릿 렌더링 시간 <500ms
- [ ] 데이터베이스 쿼리 최적화 (N+1 방지)
- [ ] 정적 자원 캐싱

### 4.2 롤아웃 계획

| Stage | 비율 | 기간 | 롤백 조건 |
|-------|------|------|----------|
| Stage 1 | 0% | 준비 | - |
| Stage 2 | 10% | 3일 | 에러율 >1% |
| Stage 3 | 50% | 3일 | 에러율 >0.5% |
| Stage 4 | 100% | 7일 | 에러율 >0.1% |

### 4.3 롤백 계획

| 상황 | 대응 | 소요 시간 |
|------|------|----------|
| 즉시 롤백 | 기능 플래그 비활성화 | 0-5분 |
| DB 롤백 | alembic downgrade -1 | 5-15분 |
| 전체 롤백 | git checkout + 배포 | 15-30분 |

---

## 의존성 그래프

```
P0-01 ─┬─▶ P0-02 ─┬─▶ P0-03 ─┬─▶ P0-05 ─▶ P0-07 ─▶ P0-08
       │          │          │           │
       │          └─▶ P0-04 ─┘           ▼
       │                              P0-10 ─▶ P0-11
       │
P0-06 ─┘

P0-12 ─▶ P0-13

[Phase 0 완료] ─▶ P1-01 ─▶ P1-02
                       ├─▶ P1-03
                       └─▶ P1-04 ─┬─▶ [그룹 A: 공통 섹션]
                                  └─▶ [그룹 B: 법인 섹션]

[Phase 1 완료] ─▶ P2-01 ─▶ P2-02 ─▶ P2-03 ─┬─▶ P2-04
                                            └─▶ P2-05

[Phase 2 완료] ─▶ P3-01 ─▶ P3-02 ─▶ P3-03 ─▶ P3-04
                       └─▶ P3-05 ─▶ P3-06 ─▶ P3-07

[Phase 3 완료] ─▶ [Phase 4: 검증 및 롤아웃]
```

---

## 병렬 실행 최적화

### 병렬 가능 작업 그룹

**Phase 0**:
- 병렬 그룹 1: P0-01 (adapters), P0-06 (profile bp), P0-09 (context_processors)
- 병렬 그룹 2: P0-03 (Employee), P0-04 (Personal) - P0-02 완료 후

**Phase 1**:
- 병렬 그룹 A: P1-05, P1-11, P1-12, P1-13, P1-14, P1-15 (공통 섹션)
- 병렬 그룹 B: P1-06~P1-10, P1-16~P1-18 (법인 전용 섹션)

**Phase 3**:
- 병렬 그룹: P3-01 (CSS), P3-05 (접근성) - 독립 작업

---

## 진행 상태 추적

### 현재 상태
- Phase 0: 대기 중
- Phase 1: 대기 중
- Phase 2: 대기 중
- Phase 3: 대기 중
- Phase 4: 대기 중

### 완료 기준
- [ ] Phase 0: 모든 인프라 코드 구현 및 import 테스트 통과
- [ ] Phase 1: 모든 템플릿 작성 및 Jinja2 문법 검증 통과
- [ ] Phase 2: 라우트 등록 및 기능 플래그 분기 동작 확인
- [ ] Phase 3: 반응형 및 접근성 테스트 통과
- [ ] Phase 4: 전체 검증 체크리스트 완료 및 롤아웃 승인

---

## 참고 문서

- `claudedocs/interface_integration_design.md` - 상세 설계 문서
- `claudedocs/interface_integration_review.md` - 다중 전문가 검토 보고서
- `claudedocs/account_interface_analysis.md` - 인터페이스 비교 분석
