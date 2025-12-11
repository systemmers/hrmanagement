# 프론트엔드 템플릿 도메인별 재설계 상세 설계서

## 문서 정보
- 작성일: 2025-12-10
- 목적: 계정 유형별 템플릿 구조를 도메인별 구조로 재설계
- 범위: templates/ 디렉터리 전체 및 Blueprint 라우트 변경

## 1. 현재 구조 분석

### 1.1 템플릿 디렉터리 구조
```
templates/
├── corporate/                    # 법인 계정 전용
│   ├── dashboard.html            # 법인 대시보드
│   ├── settings.html             # 법인 설정
│   ├── users.html                # 사용자 관리
│   ├── add_user.html             # 사용자 추가
│   └── register.html             # 법인 회원가입
├── personal/                     # 개인 계정 전용
│   ├── dashboard.html            # 개인 대시보드
│   ├── profile.html              # 프로필 조회 (deprecated)
│   ├── profile_edit.html         # 프로필 수정 (deprecated)
│   └── register.html             # 개인 회원가입
├── profile/                      # 통합된 도메인 (✅ 성공 사례)
│   ├── unified_profile.html
│   └── partials/
│       ├── _header_unified.html
│       ├── _section_nav_unified.html
│       └── sections/ (15개 섹션)
├── contracts/                    # 도메인별 (혼재)
│   ├── my_contracts.html         # 개인용
│   ├── company_contracts.html    # 법인용
│   ├── pending_contracts.html    # 개인용
│   └── company_pending.html      # 법인용
└── components/                   # 공통 컴포넌트
    └── navigation/
        ├── _sidebar_personal.html
        ├── _sidebar_corporate.html
        └── _sidebar_employee.html
```

### 1.2 문제점 분석

#### 계정 유형별 중복 코드
1. **Dashboard 중복**
   - `corporate/dashboard.html` (145줄)
   - `personal/dashboard.html` (177줄)
   - 구조적 유사성: 80% 이상 동일한 HTML 구조
   - 차이점: stats-grid 데이터만 상이

2. **Settings 중복 가능성**
   - `corporate/settings.html`: 법인 정보 관리
   - 개인 설정은 `profile_edit.html`로 분산
   - 설정 도메인 통합 필요

3. **Register 분리 유지 필요**
   - 개인/법인 회원가입은 폼 구조가 완전히 상이
   - 분리 유지가 적절함

#### 템플릿 구조 비교

| 요소 | Corporate | Personal | 통합 가능성 |
|------|-----------|----------|------------|
| 페이지 레이아웃 | base.html 상속 | base.html 상속 | ✅ 100% |
| 헤더 영역 | page-header | page-header | ✅ 100% |
| 통계 카드 | stats-grid (4개) | stats-grid (4개) | ✅ 구조 동일, 데이터만 다름 |
| 정보 카드 | info-grid | profile-summary | ⚠️ 60% (구조 유사) |
| 빠른 링크 | quick-links (4개) | quick-links (4개) | ✅ 100% |

### 1.3 Blueprint 라우트 분석

#### Corporate Blueprint (corporate.py)
```python
/corporate/dashboard      → corporate/dashboard.html
/corporate/settings       → corporate/settings.html
/corporate/users          → corporate/users.html
/corporate/add_user       → corporate/add_user.html
/corporate/register       → corporate/register.html
```

#### Personal Blueprint (personal.py)
```python
/personal/dashboard       → personal/dashboard.html
/personal/profile         → personal/profile.html (deprecated)
/personal/profile_edit    → personal/profile_edit.html (deprecated)
/personal/register        → personal/register.html
```

#### Profile Blueprint (profile/routes.py)
```python
/profile/                 → profile/unified_profile.html ✅ 성공적 통합
```

## 2. 재설계 전략

### 2.1 설계 원칙

1. **도메인 우선 원칙**
   - 계정 유형(personal/corporate)보다 기능 도메인(dashboard/settings) 우선
   - 계정별 차이는 파셜/조건문으로 처리

2. **DRY 원칙 준수**
   - 중복 코드 최소화
   - 공통 레이아웃 재사용
   - 계정별 차이는 최소한의 파셜로 분리

3. **점진적 마이그레이션**
   - 기존 파일 유지하면서 새 구조 추가
   - Blueprint 라우트 병렬 운영
   - 검증 후 구 버전 삭제

4. **롤백 가능성**
   - 모든 변경사항 추적 가능
   - 구 버전 백업 유지
   - 단계별 롤백 지점 설정

### 2.2 권장 구조 (최종안)

```
templates/
├── dashboard/                           # 🆕 도메인별 통합
│   ├── base_dashboard.html              # 공통 레이아웃
│   ├── _stats_personal.html             # 개인용 통계 파셜
│   ├── _stats_corporate.html            # 법인용 통계 파셜
│   ├── _quick_links_personal.html       # 개인용 빠른 링크
│   └── _quick_links_corporate.html      # 법인용 빠른 링크
│
├── settings/                            # 🆕 설정 도메인 통합
│   ├── base_settings.html               # 공통 설정 레이아웃
│   ├── _form_personal.html              # 개인 설정 폼
│   └── _form_corporate.html             # 법인 설정 폼
│
├── auth/                                # 유지 (계정별 분리 필요)
│   ├── login.html
│   ├── register_select.html
│   ├── register_personal.html           # 개인 회원가입
│   └── register_corporate.html          # 법인 회원가입
│
├── profile/                             # ✅ 유지 (성공적 통합 완료)
│   ├── unified_profile.html
│   └── partials/
│
├── contracts/                           # 🔄 부분 통합
│   ├── base_contracts.html              # 공통 계약 레이아웃
│   ├── _list_personal.html              # 개인 계약 목록
│   └── _list_corporate.html             # 법인 계약 목록
│
├── corporate/                           # 🔄 축소 (도메인별로 이동)
│   ├── users.html                       # 유지 (법인 전용 기능)
│   └── add_user.html                    # 유지 (법인 전용 기능)
│
├── personal/                            # 삭제 예정 (모두 도메인으로 이동)
│
└── components/                          # 유지
    ├── navigation/
    │   ├── _sidebar_unified.html        # 🆕 통합 사이드바
    │   └── _account_switcher.html       # 🆕 계정 유형 전환기
    └── shared/
        ├── _stats_card.html             # 🆕 통계 카드 컴포넌트
        └── _quick_link_grid.html        # 🆕 빠른 링크 그리드
```

### 2.3 계정 유형별 라우팅 전략

#### 방식 1: URL 유지 + 템플릿 통합 (✅ 권장)
```python
# corporate.py
@corporate_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard/base_dashboard.html',
                          account_type='corporate',
                          data=corporate_data)

# personal.py
@personal_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard/base_dashboard.html',
                          account_type='personal',
                          data=personal_data)
```

**장점:**
- 기존 URL 구조 유지 (하위 호환성)
- Blueprint 분리 유지 (권한 관리 명확)
- 템플릿 통합으로 중복 제거

**단점:**
- 라우트 함수 중복 존재

#### 방식 2: 통합 Blueprint (❌ 비권장)
```python
# dashboard.py (new)
@dashboard_bp.route('/<account_type>/dashboard')
def dashboard(account_type):
    # account_type에 따라 분기
```

**장점:**
- 라우트 함수 통합

**단점:**
- 기존 URL 구조 변경 (breaking change)
- 권한 관리 복잡도 증가
- 계정 유형별 데코레이터 적용 어려움

### 2.4 템플릿 조건 처리 방식

#### 조건문 사용 예시
```jinja2
{# dashboard/base_dashboard.html #}
{% extends "base.html" %}

{% block title %}
  {% if account_type == 'corporate' %}
    법인 대시보드 - {{ company.name }}
  {% else %}
    개인 대시보드 - 인사카드 관리 시스템
  {% endif %}
{% endblock %}

{% block content %}
<div class="page-header">
  <!-- 공통 헤더 구조 -->
</div>

<div class="dashboard-grid">
  {# 통계 카드 - 계정별 파셜 분리 #}
  {% if account_type == 'corporate' %}
    {% include 'dashboard/_stats_corporate.html' %}
  {% else %}
    {% include 'dashboard/_stats_personal.html' %}
  {% endif %}

  {# 빠른 링크 - 계정별 파셜 분리 #}
  {% if account_type == 'corporate' %}
    {% include 'dashboard/_quick_links_corporate.html' %}
  {% else %}
    {% include 'dashboard/_quick_links_personal.html' %}
  {% endif %}
</div>
{% endblock %}
```

## 3. 단계별 마이그레이션 계획

### Phase 1: Dashboard 통합 (우선순위: 높음)

#### 작업 내용
1. **새 디렉터리 생성**
   ```bash
   mkdir templates/dashboard
   ```

2. **공통 레이아웃 작성**
   - `dashboard/base_dashboard.html` 생성
   - 계정별 차이점 식별 및 파셜 분리

3. **파셜 파일 작성**
   - `_stats_personal.html`: 개인 통계 (학력/경력/자격증/어학)
   - `_stats_corporate.html`: 법인 통계 (직원수/플랜/인증상태)
   - `_quick_links_personal.html`: 개인 메뉴
   - `_quick_links_corporate.html`: 법인 메뉴

4. **Blueprint 라우트 수정**
   ```python
   # corporate.py
   def dashboard():
       return render_template('dashboard/base_dashboard.html',
                             account_type='corporate',
                             company=company)

   # personal.py
   def dashboard():
       return render_template('dashboard/base_dashboard.html',
                             account_type='personal',
                             profile=profile,
                             stats=stats)
   ```

5. **테스트 및 검증**
   - 법인 계정 대시보드 접근 테스트
   - 개인 계정 대시보드 접근 테스트
   - 스타일 일관성 확인

6. **구 버전 삭제**
   ```bash
   # 검증 완료 후
   git mv templates/corporate/dashboard.html templates/corporate/dashboard.html.bak
   git mv templates/personal/dashboard.html templates/personal/dashboard.html.bak
   ```

#### 예상 소요 시간
- 작업 시간: 2-3시간
- 테스트 시간: 1시간
- 총 소요 시간: 3-4시간

#### 위험 요소
- 템플릿 변수명 불일치 가능성
- CSS 클래스 충돌 가능성
- 계정별 데이터 구조 차이

#### 완료 조건
- [ ] 법인 대시보드 정상 렌더링
- [ ] 개인 대시보드 정상 렌더링
- [ ] 통계 데이터 정확히 표시
- [ ] 빠른 링크 정상 작동
- [ ] 스타일 일관성 유지

### Phase 2: Settings 통합 (우선순위: 중간)

#### 작업 내용
1. **현재 상태 확인**
   - 법인: `corporate/settings.html` (법인 정보 수정)
   - 개인: `personal/profile_edit.html` (프로필 수정, 사실상 설정)

2. **설정 도메인 통합 검토**
   - 법인 설정: 회사 정보, 플랜 정보
   - 개인 설정: 프로필 정보, 공개 설정

3. **통합 필요성 평가**
   - 폼 구조 유사성: 약 50%
   - 데이터 모델 완전 상이
   - **결론: 현재는 통합 보류, 추후 재검토**

#### 대안 전략
- `settings/` 디렉터리 생성하되 파일 분리 유지
- 공통 폼 컴포넌트만 추출
  - `_form_section.html`: 섹션 래퍼
  - `_form_input_group.html`: 입력 그룹

#### 예상 소요 시간
- 평가 시간: 1시간
- 컴포넌트 추출: 2시간
- 총 소요 시간: 3시간

### Phase 3: Contracts 통합 (우선순위: 중간)

#### 작업 내용
1. **현재 상태 분석**
   ```
   contracts/
   ├── my_contracts.html          # 개인용
   ├── company_contracts.html     # 법인용
   ├── pending_contracts.html     # 개인용
   └── company_pending.html       # 법인용
   ```

2. **통합 전략**
   - `base_contracts.html`: 공통 레이아웃
   - `_list_view.html`: 계약 목록 뷰 (account_type 파라미터 받음)
   - 계약 상세는 이미 통합됨 (`contract_detail.html`)

3. **라우트 수정**
   ```python
   # contracts.py
   @contracts_bp.route('/my')
   def my_contracts():
       return render_template('contracts/base_contracts.html',
                             view_type='my',
                             account_type=get_account_type())

   @contracts_bp.route('/company')
   def company_contracts():
       return render_template('contracts/base_contracts.html',
                             view_type='company',
                             account_type='corporate')
   ```

#### 예상 소요 시간
- 작업 시간: 3-4시간
- 테스트 시간: 1시간
- 총 소요 시간: 4-5시간

### Phase 4: Navigation 통합 (우선순위: 낮음)

#### 작업 내용
1. **사이드바 통합**
   - 현재: 3개 파일 (_sidebar_personal/corporate/employee)
   - 목표: 1개 파일 (_sidebar_unified.html)

2. **통합 방식**
   ```jinja2
   {# components/navigation/_sidebar_unified.html #}
   {% set account_type = session.get('account_type', 'personal') %}
   {% set user_role = session.get('user_role', 'user') %}

   <nav class="sidebar">
     {% if account_type == 'personal' %}
       <!-- 개인 메뉴 -->
     {% elif account_type == 'corporate' %}
       {% if user_role in ['admin', 'manager'] %}
         <!-- 관리자 메뉴 -->
       {% else %}
         <!-- 직원 메뉴 -->
       {% endif %}
     {% endif %}
   </nav>
   ```

3. **base.html 수정**
   ```jinja2
   {% include 'components/navigation/_sidebar_unified.html' %}
   ```

#### 예상 소요 시간
- 작업 시간: 2시간
- 테스트 시간: 1시간
- 총 소요 시간: 3시간

### Phase 5: 정리 및 문서화 (우선순위: 낮음)

#### 작업 내용
1. **구 버전 파일 삭제**
   ```bash
   rm -rf templates/corporate/dashboard.html.bak
   rm -rf templates/personal/dashboard.html.bak
   # 기타 백업 파일 정리
   ```

2. **디렉터리 구조 정리**
   - `personal/` 디렉터리 평가
   - 남은 파일들 적절한 도메인으로 이동

3. **문서 업데이트**
   - 프로젝트 구조 문서 갱신
   - 템플릿 가이드 작성
   - Blueprint 라우팅 문서 갱신

#### 예상 소요 시간
- 정리 작업: 1시간
- 문서화: 2시간
- 총 소요 시간: 3시간

## 4. Blueprint 라우트 변경 계획

### 4.1 변경 전략

#### URL 구조 유지 (권장)
```python
# 변경 전
/corporate/dashboard → corporate/dashboard.html
/personal/dashboard  → personal/dashboard.html

# 변경 후 (URL 동일, 템플릿만 변경)
/corporate/dashboard → dashboard/base_dashboard.html (account_type='corporate')
/personal/dashboard  → dashboard/base_dashboard.html (account_type='personal')
```

**장점:**
- Breaking change 없음
- 기존 북마크/링크 유지
- 점진적 마이그레이션 가능

### 4.2 Blueprint 수정 내역

#### corporate.py 수정
```python
# 변경 전
@corporate_bp.route('/dashboard')
@corporate_login_required
def dashboard():
    company_id = session.get('company_id')
    company = company_repository.get_with_stats(company_id)
    return render_template('corporate/dashboard.html', company=company)

# 변경 후
@corporate_bp.route('/dashboard')
@corporate_login_required
def dashboard():
    company_id = session.get('company_id')
    company = company_repository.get_with_stats(company_id)
    return render_template('dashboard/base_dashboard.html',
                          account_type='corporate',
                          company=company)
```

#### personal.py 수정
```python
# 변경 전
@personal_bp.route('/dashboard')
@personal_login_required
def dashboard():
    user_id = session.get('user_id')
    data = personal_service.get_dashboard_data(user_id)
    return render_template('personal/dashboard.html',
                          user=data['user'],
                          profile=data['profile'],
                          stats=data['stats'])

# 변경 후
@personal_bp.route('/dashboard')
@personal_login_required
def dashboard():
    user_id = session.get('user_id')
    data = personal_service.get_dashboard_data(user_id)
    return render_template('dashboard/base_dashboard.html',
                          account_type='personal',
                          user=data['user'],
                          profile=data['profile'],
                          stats=data['stats'])
```

### 4.3 Context Processor 추가 (선택사항)

공통 템플릿 변수를 자동 주입하여 각 라우트에서 반복 제거:

```python
# app/context_processors.py (기존 파일 수정)
@bp.app_context_processor
def inject_account_info():
    """계정 정보 자동 주입"""
    return {
        'account_type': session.get('account_type', 'personal'),
        'user_role': session.get('user_role', 'user'),
        'company_id': session.get('company_id'),
        'user_id': session.get('user_id')
    }
```

**적용 시 라우트 간소화:**
```python
# context processor 적용 후
@corporate_bp.route('/dashboard')
@corporate_login_required
def dashboard():
    company_id = session.get('company_id')
    company = company_repository.get_with_stats(company_id)
    # account_type은 context processor에서 자동 주입
    return render_template('dashboard/base_dashboard.html', company=company)
```

## 5. 롤백 계획

### 5.1 롤백 전략

#### Level 1: 템플릿 롤백 (영향도: 낮음)
**트리거:** 렌더링 오류, 스타일 깨짐

**절차:**
```bash
# 1. 백업 파일 복원
git mv templates/corporate/dashboard.html.bak templates/corporate/dashboard.html
git mv templates/personal/dashboard.html.bak templates/personal/dashboard.html

# 2. 새 파일 제거
rm -rf templates/dashboard/

# 3. Blueprint 롤백
git checkout HEAD -- app/blueprints/corporate.py
git checkout HEAD -- app/blueprints/personal.py
```

**소요 시간:** 5분

#### Level 2: Blueprint 롤백 (영향도: 중간)
**트리거:** 라우팅 오류, 권한 문제

**절차:**
```bash
# 1. Git 커밋 되돌리기
git revert <commit-hash>

# 2. 서버 재시작
supervisorctl restart hrmanagement
```

**소요 시간:** 10분

#### Level 3: 전체 롤백 (영향도: 높음)
**트리거:** 심각한 시스템 오류, 데이터 손실 위험

**절차:**
```bash
# 1. 전체 변경사항 되돌리기
git reset --hard <before-refactoring-commit>

# 2. 데이터베이스 복구 (필요시)
# (이 리팩토링은 DB 변경 없음)

# 3. 서버 재시작
supervisorctl restart hrmanagement
```

**소요 시간:** 15분

### 5.2 롤백 체크리스트

각 Phase 완료 시 롤백 가능 상태 확인:

- [ ] Git 커밋 생성됨
- [ ] 백업 파일 존재 확인
- [ ] 롤백 스크립트 테스트 완료
- [ ] 롤백 실행 권한 확인
- [ ] 영향 범위 문서화 완료

### 5.3 Rollback Point 설정

| Phase | Commit Tag | 설명 |
|-------|-----------|------|
| Phase 0 | `refactor-templates-start` | 리팩토링 시작 지점 |
| Phase 1 | `refactor-dashboard-complete` | Dashboard 통합 완료 |
| Phase 2 | `refactor-settings-complete` | Settings 평가 완료 |
| Phase 3 | `refactor-contracts-complete` | Contracts 통합 완료 |
| Phase 4 | `refactor-navigation-complete` | Navigation 통합 완료 |
| Phase 5 | `refactor-templates-complete` | 전체 리팩토링 완료 |

## 6. 테스트 계획

### 6.1 단위 테스트

#### Dashboard 테스트
```python
# tests/test_dashboard_templates.py
def test_corporate_dashboard_renders():
    """법인 대시보드 렌더링 테스트"""
    # Given
    with app.test_client() as client:
        login_as_corporate(client)

        # When
        response = client.get('/corporate/dashboard')

        # Then
        assert response.status_code == 200
        assert b'법인 대시보드' in response.data
        assert b'stats-grid' in response.data

def test_personal_dashboard_renders():
    """개인 대시보드 렌더링 테스트"""
    # Given
    with app.test_client() as client:
        login_as_personal(client)

        # When
        response = client.get('/personal/dashboard')

        # Then
        assert response.status_code == 200
        assert b'개인 대시보드' in response.data
        assert b'stats-grid' in response.data
```

#### 템플릿 변수 테스트
```python
def test_template_context_corporate():
    """법인 대시보드 컨텍스트 테스트"""
    with app.test_request_context():
        template = render_template('dashboard/base_dashboard.html',
                                  account_type='corporate',
                                  company=mock_company)

        assert 'account_type' in template
        assert template['account_type'] == 'corporate'

def test_template_context_personal():
    """개인 대시보드 컨텍스트 테스트"""
    with app.test_request_context():
        template = render_template('dashboard/base_dashboard.html',
                                  account_type='personal',
                                  profile=mock_profile,
                                  stats=mock_stats)

        assert 'account_type' in template
        assert template['account_type'] == 'personal'
```

### 6.2 통합 테스트

#### E2E 시나리오
1. **법인 계정 플로우**
   ```
   1. 법인 로그인
   2. /corporate/dashboard 접근
   3. 법인 정보 카드 표시 확인
   4. 통계 (직원수/플랜/인증) 확인
   5. 빠른 링크 (직원관리/설정) 확인
   ```

2. **개인 계정 플로우**
   ```
   1. 개인 로그인
   2. /personal/dashboard 접근
   3. 프로필 요약 표시 확인
   4. 통계 (학력/경력/자격증/어학) 확인
   5. 빠른 링크 (프로필수정 등) 확인
   ```

3. **계정 전환 플로우**
   ```
   1. 법인 로그인
   2. Dashboard 접근
   3. 로그아웃
   4. 개인 로그인
   5. Dashboard 접근
   6. 올바른 계정 유형 표시 확인
   ```

### 6.3 성능 테스트

#### 렌더링 성능
```python
import time

def test_dashboard_rendering_performance():
    """대시보드 렌더링 성능 테스트"""
    with app.test_client() as client:
        login_as_corporate(client)

        start = time.time()
        for _ in range(100):
            client.get('/corporate/dashboard')
        elapsed = time.time() - start

        avg_time = elapsed / 100
        assert avg_time < 0.1  # 100ms 이하
```

#### 템플릿 캐싱 효과
```python
def test_template_caching():
    """통합 템플릿 캐싱 효과 테스트"""
    # 첫 렌더링 (캐시 미스)
    start = time.time()
    render_template('dashboard/base_dashboard.html', account_type='corporate')
    first_render = time.time() - start

    # 두 번째 렌더링 (캐시 히트)
    start = time.time()
    render_template('dashboard/base_dashboard.html', account_type='personal')
    second_render = time.time() - start

    # 캐싱으로 인한 성능 향상 확인
    assert second_render < first_render * 0.5
```

### 6.4 UI/UX 테스트

#### 체크리스트
- [ ] 법인 대시보드 레이아웃 일관성
- [ ] 개인 대시보드 레이아웃 일관성
- [ ] 반응형 디자인 (모바일/태블릿/데스크톱)
- [ ] 브라우저 호환성 (Chrome/Firefox/Safari/Edge)
- [ ] 접근성 (ARIA 레이블, 키보드 탐색)
- [ ] 다크 모드 지원 (있다면)

#### 스크린샷 비교
```bash
# 리팩토링 전 스크린샷 캡처
playwright screenshot /corporate/dashboard --output before-corp.png
playwright screenshot /personal/dashboard --output before-pers.png

# 리팩토링 후 스크린샷 캡처
playwright screenshot /corporate/dashboard --output after-corp.png
playwright screenshot /personal/dashboard --output after-pers.png

# 픽셀 차이 비교
compare before-corp.png after-corp.png diff-corp.png
```

### 6.5 보안 테스트

#### 권한 검증
```python
def test_corporate_dashboard_requires_auth():
    """법인 대시보드 인증 필요"""
    with app.test_client() as client:
        response = client.get('/corporate/dashboard')
        assert response.status_code == 302  # Redirect to login

def test_personal_cannot_access_corporate():
    """개인 계정이 법인 대시보드 접근 불가"""
    with app.test_client() as client:
        login_as_personal(client)
        response = client.get('/corporate/dashboard')
        assert response.status_code == 403  # Forbidden
```

#### XSS 방지
```python
def test_dashboard_escapes_user_input():
    """사용자 입력 이스케이프 테스트"""
    malicious_name = "<script>alert('XSS')</script>"

    with app.test_client() as client:
        login_as_personal(client)
        # 악의적인 이름으로 프로필 생성
        create_profile(name=malicious_name)

        response = client.get('/personal/dashboard')
        # 스크립트가 실행되지 않고 이스케이프되어야 함
        assert b'<script>' not in response.data
        assert b'&lt;script&gt;' in response.data
```

## 7. 예상 효과

### 7.1 코드 중복 감소

| 항목 | 변경 전 | 변경 후 | 감소율 |
|------|---------|---------|--------|
| Dashboard 템플릿 | 322줄 (2파일) | 180줄 (1파일 + 파셜) | 44% 감소 |
| Settings 템플릿 | 340줄 (2파일) | 예상 200줄 | 41% 감소 |
| Contracts 템플릿 | 520줄 (4파일) | 예상 300줄 | 42% 감소 |
| Navigation 컴포넌트 | 450줄 (3파일) | 예상 200줄 | 56% 감소 |
| **총합** | **1,632줄** | **880줄** | **46% 감소** |

### 7.2 유지보수성 향상

#### 변경 전
```
스타일 수정 시:
1. corporate/dashboard.html 수정
2. personal/dashboard.html 수정
3. 일관성 검증
총 작업: 3단계
```

#### 변경 후
```
스타일 수정 시:
1. dashboard/base_dashboard.html 수정
총 작업: 1단계
```

**생산성 향상:** 66% (3단계 → 1단계)

### 7.3 일관성 향상

#### 계정 유형 간 UI 일관성
- 변경 전: 각 계정별로 독립적인 디자인 → 불일치 발생
- 변경 후: 공통 레이아웃 사용 → 자동 일관성 유지

#### 디자인 시스템 적용 용이성
- 변경 전: 여러 파일 수정 필요
- 변경 후: 중앙 집중식 관리

### 7.4 성능 영향

#### 템플릿 캐싱 효율
- 변경 전: 각 계정별 템플릿 개별 캐싱
- 변경 후: 공통 레이아웃 한 번 캐싱 → 메모리 절약

#### 예상 성능 지표
- 템플릿 렌더링 시간: ±5% (거의 동일)
- 메모리 사용량: -20% (캐시 중복 제거)
- 초기 로딩 시간: -10% (파일 수 감소)

## 8. 구현 예시 코드

### 8.1 Dashboard 통합 템플릿

#### dashboard/base_dashboard.html
```jinja2
{% extends "base.html" %}

{% block title %}
  {% if account_type == 'corporate' %}
    법인 대시보드 - {{ company.name }}
  {% else %}
    개인 대시보드 - 인사카드 관리 시스템
  {% endif %}
{% endblock %}

{% block content %}
<div class="page-header">
  <div class="page-title-row">
    <h1 class="page-title">
      {% if account_type == 'corporate' %}법인 대시보드{% else %}개인 대시보드{% endif %}
    </h1>
    <div class="page-actions">
      {% if account_type == 'corporate' %}
        {% if session.get('user_role') in ['admin', 'manager'] %}
        <a href="{{ url_for('corporate.settings') }}" class="btn btn-secondary">
          <i class="fas fa-cog"></i>
          <span>설정</span>
        </a>
        {% endif %}
      {% else %}
        <a href="{{ url_for('personal.profile') }}" class="btn btn-secondary">
          <i class="fas fa-user"></i>
          <span>프로필 보기</span>
        </a>
        <a href="{{ url_for('personal.profile_edit') }}" class="btn btn-primary">
          <i class="fas fa-edit"></i>
          <span>프로필 수정</span>
        </a>
      {% endif %}
    </div>
  </div>
  <p class="page-description">
    {% if account_type == 'corporate' %}
      {{ company.name }} 관리 현황
    {% else %}
      {{ profile.name }}님, 환영합니다!
    {% endif %}
  </p>
</div>

<div class="dashboard-grid">
  {# 첫 번째 카드: 정보 요약 #}
  <div class="dashboard-card">
    <div class="card-header">
      <h2 class="card-title">
        <i class="fas fa-{% if account_type == 'corporate' %}info-circle{% else %}user-circle{% endif %}"></i>
        {% if account_type == 'corporate' %}법인 정보{% else %}프로필 요약{% endif %}
      </h2>
    </div>
    <div class="card-body">
      {% if account_type == 'corporate' %}
        {% include 'dashboard/_info_corporate.html' %}
      {% else %}
        {% include 'dashboard/_info_personal.html' %}
      {% endif %}
    </div>
  </div>

  {# 두 번째 카드: 통계 #}
  <div class="dashboard-card">
    <div class="card-header">
      <h2 class="card-title">
        <i class="fas fa-chart-bar"></i>
        {% if account_type == 'corporate' %}현황{% else %}이력 현황{% endif %}
      </h2>
    </div>
    <div class="card-body">
      <div class="stats-grid">
        {% if account_type == 'corporate' %}
          {% include 'dashboard/_stats_corporate.html' %}
        {% else %}
          {% include 'dashboard/_stats_personal.html' %}
        {% endif %}
      </div>
    </div>
  </div>

  {# 세 번째 카드: 빠른 링크 #}
  <div class="dashboard-card quick-links-card">
    <div class="card-header">
      <h2 class="card-title">
        <i class="fas fa-bolt"></i>
        빠른 메뉴
      </h2>
    </div>
    <div class="card-body">
      <div class="quick-links">
        {% if account_type == 'corporate' %}
          {% include 'dashboard/_quick_links_corporate.html' %}
        {% else %}
          {% include 'dashboard/_quick_links_personal.html' %}
        {% endif %}
      </div>
    </div>
  </div>

  {# 네 번째 카드: 추가 정보 (계정별 차이) #}
  {% if account_type == 'personal' %}
  <div class="dashboard-card">
    <div class="card-header">
      <h2 class="card-title">
        <i class="fas fa-eye"></i>
        공개 설정
      </h2>
    </div>
    <div class="card-body">
      {% include 'dashboard/_visibility_status.html' %}
    </div>
  </div>
  {% endif %}
</div>

<!-- CSS moved to: components/dashboard.css, info-grid.css, stats-cards.css, quick-links.css -->
{% endblock %}
```

#### dashboard/_stats_corporate.html
```jinja2
{# 법인용 통계 파셜 #}
<div class="stat-item">
  <div class="stat-icon employees">
    <i class="fas fa-users"></i>
  </div>
  <div class="stat-content">
    <span class="stat-value">{{ company.employee_count }}</span>
    <span class="stat-label">등록 직원</span>
  </div>
</div>

<div class="stat-item">
  <div class="stat-icon limit">
    <i class="fas fa-user-plus"></i>
  </div>
  <div class="stat-content">
    <span class="stat-value">{{ company.max_employees }}</span>
    <span class="stat-label">최대 인원</span>
  </div>
</div>

<div class="stat-item">
  <div class="stat-icon plan">
    <i class="fas fa-crown"></i>
  </div>
  <div class="stat-content">
    <span class="stat-value">{{ company.plan_label }}</span>
    <span class="stat-label">현재 플랜</span>
  </div>
</div>

<div class="stat-item">
  <div class="stat-icon status {% if company.is_verified %}verified{% else %}pending{% endif %}">
    <i class="fas fa-{% if company.is_verified %}check-circle{% else %}clock{% endif %}"></i>
  </div>
  <div class="stat-content">
    <span class="stat-value">{% if company.is_verified %}인증됨{% else %}대기중{% endif %}</span>
    <span class="stat-label">인증 상태</span>
  </div>
</div>
```

#### dashboard/_stats_personal.html
```jinja2
{# 개인용 통계 파셜 #}
<div class="stat-item">
  <div class="stat-icon education">
    <i class="fas fa-graduation-cap"></i>
  </div>
  <div class="stat-content">
    <span class="stat-value">{{ stats.education_count }}</span>
    <span class="stat-label">학력</span>
  </div>
</div>

<div class="stat-item">
  <div class="stat-icon career">
    <i class="fas fa-briefcase"></i>
  </div>
  <div class="stat-content">
    <span class="stat-value">{{ stats.career_count }}</span>
    <span class="stat-label">경력</span>
  </div>
</div>

<div class="stat-item">
  <div class="stat-icon certificate">
    <i class="fas fa-certificate"></i>
  </div>
  <div class="stat-content">
    <span class="stat-value">{{ stats.certificate_count }}</span>
    <span class="stat-label">자격증</span>
  </div>
</div>

<div class="stat-item">
  <div class="stat-icon language">
    <i class="fas fa-language"></i>
  </div>
  <div class="stat-content">
    <span class="stat-value">{{ stats.language_count }}</span>
    <span class="stat-label">어학</span>
  </div>
</div>
```

#### dashboard/_quick_links_corporate.html
```jinja2
{# 법인용 빠른 링크 #}
<a href="{{ url_for('employees.employee_list') }}" class="quick-link">
  <i class="fas fa-users"></i>
  <span>직원 목록</span>
</a>
<a href="{{ url_for('employees.employee_new') }}" class="quick-link">
  <i class="fas fa-user-plus"></i>
  <span>직원 등록</span>
</a>
{% if session.get('user_role') in ['admin', 'manager'] %}
<a href="{{ url_for('corporate.users') }}" class="quick-link">
  <i class="fas fa-user-cog"></i>
  <span>사용자 관리</span>
</a>
<a href="{{ url_for('corporate.settings') }}" class="quick-link">
  <i class="fas fa-building"></i>
  <span>법인 설정</span>
</a>
{% endif %}
```

#### dashboard/_quick_links_personal.html
```jinja2
{# 개인용 빠른 링크 #}
<a href="{{ url_for('personal.profile_edit') }}" class="quick-link">
  <i class="fas fa-user-edit"></i>
  <span>프로필 수정</span>
</a>
<a href="{{ url_for('personal.profile') }}#education" class="quick-link">
  <i class="fas fa-graduation-cap"></i>
  <span>학력 관리</span>
</a>
<a href="{{ url_for('personal.profile') }}#career" class="quick-link">
  <i class="fas fa-briefcase"></i>
  <span>경력 관리</span>
</a>
<a href="{{ url_for('personal.profile') }}#certificate" class="quick-link">
  <i class="fas fa-certificate"></i>
  <span>자격증 관리</span>
</a>
```

### 8.2 Blueprint 수정 예시

#### app/blueprints/corporate.py
```python
@corporate_bp.route('/dashboard')
@corporate_login_required
def dashboard():
    """법인 대시보드 (통합 템플릿 사용)"""
    company_id = session.get('company_id')
    if not company_id:
        flash('법인 정보를 찾을 수 없습니다.', 'error')
        return redirect(url_for('main.index'))

    company = company_repository.get_with_stats(company_id)
    if not company:
        flash('법인 정보를 찾을 수 없습니다.', 'error')
        return redirect(url_for('main.index'))

    # 통합 템플릿 사용 (account_type 전달)
    return render_template('dashboard/base_dashboard.html',
                          account_type='corporate',
                          company=company)
```

#### app/blueprints/personal.py
```python
@personal_bp.route('/dashboard')
@personal_login_required
def dashboard():
    """개인 대시보드 (통합 템플릿 사용)"""
    user_id = session.get('user_id')
    data = personal_service.get_dashboard_data(user_id)

    if not data:
        flash('사용자 정보를 찾을 수 없습니다.', 'error')
        return redirect(url_for('main.index'))

    if not data['profile']:
        flash('프로필을 먼저 작성해주세요.', 'info')
        return redirect(url_for('personal.profile_edit'))

    # 통합 템플릿 사용 (account_type 전달)
    return render_template('dashboard/base_dashboard.html',
                          account_type='personal',
                          user=data['user'],
                          profile=data['profile'],
                          stats=data['stats'])
```

### 8.3 Context Processor (선택사항)

#### app/context_processors.py
```python
from flask import session

def inject_account_context():
    """계정 정보 자동 주입"""
    return {
        'account_type': session.get('account_type', 'personal'),
        'user_role': session.get('user_role', 'user'),
        'company_id': session.get('company_id'),
        'user_id': session.get('user_id'),
        'is_corporate': session.get('account_type') == 'corporate',
        'is_personal': session.get('account_type') == 'personal',
        'is_admin': session.get('user_role') in ['admin', 'manager']
    }

# app/__init__.py에 등록
def create_app():
    # ...
    from app.context_processors import inject_account_context
    app.context_processor(inject_account_context)
    # ...
```

**적용 후 템플릿 간소화:**
```jinja2
{# context processor 적용 후 #}
{% if is_corporate %}
  <!-- 법인 전용 콘텐츠 -->
{% else %}
  <!-- 개인 전용 콘텐츠 -->
{% endif %}

{# 기존 방식 #}
{% if account_type == 'corporate' %}
  <!-- 법인 전용 콘텐츠 -->
{% else %}
  <!-- 개인 전용 콘텐츠 -->
{% endif %}
```

## 9. 완료 조건

### 9.1 Phase별 완료 조건

#### Phase 1: Dashboard 통합
- [ ] `dashboard/base_dashboard.html` 작성 완료
- [ ] 법인/개인 파셜 파일 작성 완료
- [ ] Blueprint 라우트 수정 완료
- [ ] 법인 계정 대시보드 정상 작동
- [ ] 개인 계정 대시보드 정상 작동
- [ ] 단위 테스트 통과
- [ ] UI/UX 일관성 검증
- [ ] Git 커밋 및 태그 생성

#### Phase 2: Settings 평가
- [ ] 설정 도메인 통합 필요성 평가 완료
- [ ] 공통 폼 컴포넌트 식별
- [ ] 구현 방향 결정 (통합 vs 분리)
- [ ] 문서화 완료

#### Phase 3: Contracts 통합
- [ ] `contracts/base_contracts.html` 작성
- [ ] 계약 목록 뷰 통합
- [ ] Blueprint 라우트 수정
- [ ] 테스트 통과
- [ ] Git 커밋 및 태그 생성

#### Phase 4: Navigation 통합
- [ ] `_sidebar_unified.html` 작성
- [ ] base.html 수정
- [ ] 계정 유형별 메뉴 테스트
- [ ] Git 커밋 및 태그 생성

#### Phase 5: 정리 및 문서화
- [ ] 구 버전 파일 삭제
- [ ] 디렉터리 구조 정리
- [ ] 프로젝트 문서 업데이트
- [ ] 최종 검증 완료

### 9.2 전체 완료 조건
- [ ] 모든 Phase 완료
- [ ] 통합 테스트 통과
- [ ] 성능 저하 없음 (±5% 이내)
- [ ] 코드 중복 40% 이상 감소
- [ ] 문서화 완료
- [ ] 팀 리뷰 승인

## 10. 참고 자료

### 10.1 관련 문서
- `profile/` 통합 사례: 이미 성공적으로 완료된 도메인별 통합 예시
- Flask 템플릿 가이드: https://flask.palletsprojects.com/en/latest/templating/
- Jinja2 템플릿 상속: https://jinja.palletsprojects.com/en/latest/templates/#template-inheritance

### 10.2 프로젝트 컨벤션
- 파일명: `snake_case.html`
- 파셜 파일: `_prefix_name.html` (언더스코어로 시작)
- 디렉터리: 도메인명 (소문자)
- 템플릿 변수: `snake_case`

### 10.3 코드 리뷰 체크리스트
- [ ] 중복 코드 제거됨
- [ ] 계정별 분기 로직 명확함
- [ ] 성능 저하 없음
- [ ] 보안 이슈 없음
- [ ] 접근성 유지됨
- [ ] 반응형 디자인 유지됨
- [ ] 브라우저 호환성 유지됨

## 11. 리스크 관리

### 11.1 기술적 리스크

| 리스크 | 영향도 | 발생 가능성 | 완화 전략 |
|--------|--------|-------------|----------|
| 템플릿 변수명 불일치 | 높음 | 중간 | 변수명 매핑 문서 작성, 단위 테스트 |
| CSS 클래스 충돌 | 중간 | 낮음 | 네임스페이스 규칙 준수 |
| 성능 저하 | 중간 | 낮음 | 성능 테스트, 캐싱 전략 |
| 보안 취약점 | 높음 | 낮음 | 보안 테스트, 코드 리뷰 |
| 브라우저 호환성 문제 | 낮음 | 낮음 | 크로스 브라우저 테스트 |

### 11.2 운영 리스크

| 리스크 | 영향도 | 발생 가능성 | 완화 전략 |
|--------|--------|-------------|----------|
| 서비스 다운타임 | 높음 | 낮음 | 무중단 배포, 롤백 계획 |
| 사용자 불만 | 중간 | 낮음 | UI 일관성 유지, A/B 테스트 |
| 데이터 손실 | 높음 | 매우 낮음 | 데이터베이스 변경 없음 |
| 팀 저항 | 중간 | 중간 | 사전 교육, 문서화 |

### 11.3 리스크 모니터링

#### 배포 후 모니터링 항목
- [ ] 에러 로그 확인 (첫 24시간)
- [ ] 사용자 피드백 수집 (첫 1주일)
- [ ] 성능 메트릭 모니터링 (첫 1개월)
- [ ] A/B 테스트 결과 분석 (필요시)

## 12. 일정 및 리소스

### 12.1 예상 일정

| Phase | 작업 시간 | 테스트 시간 | 총 소요 시간 |
|-------|----------|------------|-------------|
| Phase 0 (준비) | 1시간 | - | 1시간 |
| Phase 1 (Dashboard) | 3시간 | 1시간 | 4시간 |
| Phase 2 (Settings) | 2시간 | 1시간 | 3시간 |
| Phase 3 (Contracts) | 4시간 | 1시간 | 5시간 |
| Phase 4 (Navigation) | 2시간 | 1시간 | 3시간 |
| Phase 5 (정리) | 2시간 | 1시간 | 3시간 |
| **총합** | **14시간** | **5시간** | **19시간** |

### 12.2 리소스 할당

#### 인력
- 프론트엔드 개발자: 1명 (14시간)
- 백엔드 개발자: 0.5명 (7시간, Blueprint 수정)
- QA 엔지니어: 0.5명 (5시간, 테스트)
- 총 인력: 2 FTE

#### 도구
- 개발 환경: VS Code, Flask 개발 서버
- 테스트: pytest, Playwright
- 버전 관리: Git
- 협업: GitHub, Slack

### 12.3 마일스톤

| 날짜 | 마일스톤 | 완료 조건 |
|------|---------|----------|
| D+1 | Phase 1 완료 | Dashboard 통합 및 테스트 |
| D+2 | Phase 2-3 완료 | Settings 평가, Contracts 통합 |
| D+3 | Phase 4-5 완료 | Navigation 통합, 정리 |
| D+4 | 최종 검증 | 통합 테스트, 코드 리뷰 |
| D+5 | 프로덕션 배포 | 모니터링 시작 |

## 13. 결론

### 13.1 요약
본 설계서는 HRManagement 프로젝트의 템플릿 구조를 계정 유형별 구조에서 도메인별 구조로 재설계하는 방법을 제시합니다. 주요 목표는:
- 코드 중복 46% 감소
- 유지보수성 66% 향상
- UI 일관성 자동 보장

### 13.2 핵심 전략
1. **도메인 우선 원칙**: 기능(dashboard/settings)이 계정 유형(personal/corporate)보다 우선
2. **점진적 마이그레이션**: 기존 시스템 유지하면서 단계적 전환
3. **롤백 가능성**: 각 단계별 롤백 지점 설정

### 13.3 기대 효과
- **개발 속도 향상**: 중복 코드 제거로 수정 작업 66% 감소
- **품질 향상**: 통합 템플릿으로 일관성 자동 유지
- **확장성 향상**: 새 계정 유형 추가 시 파셜만 추가하면 됨

### 13.4 다음 단계
1. 팀 리뷰 및 승인
2. Phase 1 (Dashboard 통합) 시작
3. 단계별 진행 및 피드백 수렴
4. 최종 검증 및 배포

---

**문서 버전:** 1.0
**최종 수정:** 2025-12-10
**작성자:** Claude (AI Assistant)
**검토자:** (검토 후 기입)
