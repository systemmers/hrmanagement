# HR Management 시스템 구현 워크플로우

## 개요
- **생성일**: 2025-12-10
- **기반**: 코드 분석 보고서 (Frontend/Backend/Refactoring Expert)
- **모드**: --safe (보수적 접근, 점진적 개선)
- **총 예상 시간**: 30시간 (3 Sprint)

---

## 워크플로우 구조

```
Sprint 1: Quick Wins (8h)     Sprint 2: 코드 품질 (11h)    Sprint 3: 구조 개선 (11h)
├── 데코레이터 통합 (2h)       ├── 헬퍼 함수 일반화 (6h)     ├── sync_service 분할 (8h)
├── camelCase 최적화 (2h)     ├── CSS 분할 (2h)            └── 접근성 강화 (3h)
└── TODO 완료 (4h)            └── 템플릿 통합 (3h)
```

---

## Sprint 1: Quick Wins (1주차)

### 사전 작업
```bash
git checkout -b refactor/code-quality-improvements
```

### Task 1.1: 데코레이터 통합
| 항목 | 내용 |
|------|------|
| **시간** | 2시간 |
| **위험도** | Low |
| **파일** | `app/blueprints/audit.py`, `app/utils/decorators.py` |

**작업 내용:**
- [ ] `audit.py:18-48`의 중복 데코레이터 제거
- [ ] `decorators.py`에서 import로 변경
- [ ] API 전용 데코레이터 분리 (필요시)

**검증:**
```bash
# 서버 실행 후 감사 로그 API 테스트
curl http://localhost:5000/api/audit/logs
```

**롤백:**
```bash
git checkout -- app/blueprints/audit.py
```

---

### Task 1.2: camelCase 처리 최적화
| 항목 | 내용 |
|------|------|
| **시간** | 2시간 |
| **위험도** | Low |
| **파일** | `app/utils/template_helpers.py`, `app/models/employee.py` |

**작업 내용:**
- [ ] Flask 템플릿 필터 `to_camel_case` 생성
- [ ] `employee.py:83-124` to_dict() 중복 필드 제거
- [ ] 템플릿에서 필터 사용으로 변경

**검증:**
```bash
# 직원 상세 페이지 렌더링 확인
http://localhost:5000/employees/1
```

---

### Task 1.3: TODO 주석 완료
| 항목 | 내용 |
|------|------|
| **시간** | 4시간 |
| **위험도** | Medium |
| **파일** | `app/utils/context_processors.py:56`, `app/models/user.py:111` |

**작업 내용:**
- [ ] 매니저 부서 직원 확인 로직 구현
- [ ] 접근 제어 검증 함수 작성
- [ ] 테스트 케이스 추가

**검증:**
```python
# 매니저 권한으로 다른 부서 직원 접근 시 거부 확인
```

---

## Sprint 2: 코드 품질 개선 (2주차)

### Task 2.1: 헬퍼 함수 일반화
| 항목 | 내용 |
|------|------|
| **시간** | 6시간 |
| **위험도** | Medium |
| **파일** | `app/blueprints/employees/helpers.py` |

**작업 내용:**
- [ ] `RelatedDataUpdater` 클래스 생성
- [ ] 6개 `update_*_data()` 함수 통합:
  - `update_family_data()` (185-212)
  - `update_education_data()` (214-240)
  - `update_career_data()` (241-267)
  - `update_certificate_data()` (268-294)
  - `update_language_data()` (295-319)
  - `update_military_data()` (320-339)

**새 구조:**
```python
class RelatedDataUpdater:
    def update(self, employee_id, form_data, config):
        # config = {
        #     'repo': education_repo,
        #     'model': Education,
        #     'field_groups': {'school_name': 'school_name', ...},
        #     'primary_field': 'school_name'
        # }
```

**예상 감소:** 150줄

**검증:**
```bash
# 직원 등록/수정 폼에서 교육, 경력, 자격증 저장 테스트
```

---

### Task 2.2: CSS 대파일 분할
| 항목 | 내용 |
|------|------|
| **시간** | 2시간 |
| **위험도** | Low |
| **파일** | `app/static/css/components/salary-calculator.css` (879줄) |

**작업 내용:**
- [ ] `salary-calculator-modal.css` 생성 (모달 구조)
- [ ] `salary-calculator-form.css` 생성 (입력 필드)
- [ ] `salary-calculator-result.css` 생성 (결과 표시)
- [ ] `base.html`에서 import 수정

**검증:**
```bash
# 급여 계산기 모달 열기 및 계산 테스트
```

---

### Task 2.3: 템플릿 중복 제거
| 항목 | 내용 |
|------|------|
| **시간** | 3시간 |
| **위험도** | Medium |
| **파일** | `app/templates/partials/*_section_nav*.html` (5개 파일) |

**작업 내용:**
- [ ] 통합 `_section_nav.html` 매크로 생성
- [ ] 역할별 옵션 파라미터 추가
- [ ] 기존 5개 파일에서 매크로 호출로 변경:
  - `employee_detail/_section_nav.html`
  - `employee_detail/_section_nav_basic.html`
  - `employee_detail/_section_nav_history.html`
  - `employee_form/_section_nav.html`
  - `profile/partials/_section_nav_unified.html`

**새 구조:**
```jinja2
{% macro section_nav(sections, active_section, mode='detail', show_history=false) %}
  {# 통합된 섹션 네비게이션 #}
{% endmacro %}
```

**검증:**
```bash
# 직원 상세, 직원 폼, 프로필 페이지에서 섹션 네비 동작 확인
```

---

## Sprint 3: 구조적 개선 (3주차)

### Task 3.1: sync_service 분할
| 항목 | 내용 |
|------|------|
| **시간** | 8시간 |
| **위험도** | High |
| **파일** | `app/services/sync_service.py` (985줄) |

**작업 내용:**
- [ ] `BasicFieldSync` 클래스 (기본 필드 동기화, 250줄)
- [ ] `RelationSync` 클래스 (관계형 데이터, 250줄)
- [ ] `SnapshotSync` 클래스 (스냅샷 기능, 200줄)
- [ ] `SyncService` (조정자, 300줄)

**새 구조:**
```
app/services/
├── sync/
│   ├── __init__.py
│   ├── basic_field_sync.py
│   ├── relation_sync.py
│   └── snapshot_sync.py
└── sync_service.py (기존 인터페이스 유지)
```

**검증:**
```bash
# 계약 승인 → 데이터 동기화 플로우 테스트
# 1. 법인 계정으로 계약 요청
# 2. 개인 계정으로 승인
# 3. 동기화 확인
```

**롤백 계획:**
```bash
# 단계별 커밋으로 특정 지점 롤백 가능
git log --oneline
git revert <commit-hash>
```

---

### Task 3.2: 접근성 강화
| 항목 | 내용 |
|------|------|
| **시간** | 3시간 |
| **위험도** | Low |
| **파일** | 전체 템플릿 |

**작업 내용:**
- [ ] 모든 `form-input`에 `aria-describedby` 추가
- [ ] 필수 필드에 `aria-required="true"` 추가
- [ ] 버튼에 `aria-label` 추가
- [ ] 포커스 스타일 강화

**우선 대상:**
1. `macros/_form_controls.html`
2. `employees/employee_form.html`
3. `personal/register.html`
4. `corporate/register.html`

**검증:**
```bash
# Lighthouse 접근성 점수 확인
# Chrome DevTools > Lighthouse > Accessibility
```

---

## 의존성 맵

```
Task 1.1 (데코레이터) ─────────────────────────────────┐
                                                      │
Task 1.2 (camelCase) ──────────────────────────────┐  │
                                                   │  │
Task 1.3 (TODO) ────────────────────────────────┐  │  │
                                                │  │  │
                                                v  v  v
Task 2.1 (헬퍼 일반화) ───────> Task 3.1 (sync_service)
                                                │
Task 2.2 (CSS 분할) ─────────────────────────>  │
                                                │
Task 2.3 (템플릿 통합) ──────────────────────>  │
                                                v
                                     Task 3.2 (접근성)
```

---

## 체크리스트 요약

### Sprint 1 (8h)
- [ ] git branch 생성
- [ ] Task 1.1: 데코레이터 통합 완료
- [ ] Task 1.2: camelCase 최적화 완료
- [ ] Task 1.3: TODO 주석 완료
- [ ] Sprint 1 검증 완료
- [ ] git commit & push

### Sprint 2 (11h)
- [ ] Task 2.1: 헬퍼 함수 일반화 완료
- [ ] Task 2.2: CSS 분할 완료
- [ ] Task 2.3: 템플릿 통합 완료
- [ ] Sprint 2 검증 완료
- [ ] git commit & push

### Sprint 3 (11h)
- [ ] Task 3.1: sync_service 분할 완료
- [ ] Task 3.2: 접근성 강화 완료
- [ ] 전체 회귀 테스트
- [ ] PR 생성 및 리뷰
- [ ] main 브랜치 머지

---

## 예상 결과

| 지표 | 현재 | 목표 | 개선율 |
|------|------|------|--------|
| 코드 라인 | 41,000 | 40,700 | -300줄 |
| 중복 코드 | 높음 | 중간 | -50% |
| 유지보수성 | B | B+ | +25% |
| 접근성 점수 | 60% | 90%+ | +50% |

---

## 장기 계획 (별도 Sprint)

다음 작업은 별도 기능 브랜치에서 진행:

1. **DI 컨테이너 도입** (8h)
   - flask-injector 설치
   - Extensions 전역 변수 제거
   - 테스트 환경 구성

2. **JWT 인증 전환** (8h)
   - PyJWT 도입
   - 세션 → 토큰 마이그레이션
   - CSRF 보안 강화

3. **Employee 모델 분할** (12h)
   - EmployeeBasic / EmployeeExtended
   - DB 마이그레이션 계획
   - 기존 쿼리 호환성 유지

---

## 명령어 참조

```bash
# 워크플로우 시작
git checkout -b refactor/code-quality-improvements

# Sprint 완료 후 커밋
git add .
git commit -m "refactor: Sprint 1 - Quick Wins (데코레이터, camelCase, TODO)"

# PR 생성
gh pr create --title "Refactor: Code Quality Improvements" --body "..."

# 롤백 (필요시)
git revert HEAD~3..HEAD
```

