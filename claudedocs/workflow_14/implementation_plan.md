# 템플릿 통합 구현 계획서

## 개요

본 문서는 dev_prompt.md #3 요구사항에 따른 템플릿 통합 구현 계획을 정의합니다.

## 요구사항 요약

1. 법인 계정 템플릿을 공통 템플릿으로 사용
2. 프로필 기능을 공통 템플릿에 포함
3. 일반 개인 계정도 employee 템플릿 스타일로 통합
4. 기존 구축된 템플릿 최대 활용

## 구현 순서

### Sprint 1: 프로필 통합 (Phase 1)

#### 1.1 personal.profile 라우트 수정

**파일**: `app/blueprints/personal.py`

**현재 상태**:
```python
@personal_bp.route('/profile')
@login_required
def profile():
    profile = PersonalProfile.query.filter_by(user_id=current_user.id).first()
    return render_template('personal/profile.html', profile=profile)
```

**변경 후**:
```python
from app.adapters.profile_adapter import PersonalProfileAdapter

@personal_bp.route('/profile')
@login_required
def profile():
    profile = PersonalProfile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        flash('프로필이 없습니다. 먼저 프로필을 생성해주세요.', 'warning')
        return redirect(url_for('personal.dashboard'))

    adapter = PersonalProfileAdapter(profile)

    context = {
        'is_corporate': False,
        'profile_name': adapter.get_display_name(),
        'basic_info': adapter.get_basic_info(),
        'organization_info': None,
        'contract_info': None,
        'salary_info': None,
        'benefit_info': None,
        'insurance_info': None,
        'education_list': adapter.get_education_list(),
        'career_list': adapter.get_career_list(),
        'certificate_list': adapter.get_certificate_list(),
        'language_list': adapter.get_language_list(),
        'military_info': adapter.get_military_info(),
        'sections': adapter.get_available_sections(),
    }

    return render_template('profile/unified_profile.html', **context)
```

#### 1.2 템플릿 컨텍스트 변수 매핑

| 기존 (personal/profile.html) | 통합 (unified_profile.html) |
|------------------------------|----------------------------|
| profile.name | basic_info['name'] |
| profile.educations | education_list |
| profile.careers | career_list |
| profile.certificates | certificate_list |
| profile.languages | language_list |
| profile.military_service | military_info |

#### 1.3 테스트 체크리스트

- [ ] 개인 계정 로그인 후 프로필 페이지 접근
- [ ] 기본 정보 표시 확인
- [ ] 학력/경력/자격증/어학/병역 정보 표시 확인
- [ ] 법인 전용 섹션이 숨겨지는지 확인
- [ ] 프로필 수정 링크 동작 확인

### Sprint 2: 대시보드 통합 (Phase 2)

#### 2.1 personal.dashboard 라우트 수정

**파일**: `app/blueprints/personal.py`

**현재 상태**:
```python
@personal_bp.route('/dashboard')
@login_required
def dashboard():
    profile = PersonalProfile.query.filter_by(user_id=current_user.id).first()
    stats = get_personal_stats(profile)
    return render_template('personal/dashboard.html', profile=profile, stats=stats)
```

**변경 후**:
```python
@personal_bp.route('/dashboard')
@login_required
def dashboard():
    profile = PersonalProfile.query.filter_by(user_id=current_user.id).first()
    stats = get_personal_stats(profile)
    return render_template('dashboard/base_dashboard.html',
        account_type='personal',
        profile=profile,
        stats=stats
    )
```

#### 2.2 corporate.dashboard 라우트 수정

**파일**: `app/blueprints/corporate.py`

**현재 상태**:
```python
@corporate_bp.route('/dashboard')
@login_required
def dashboard():
    company = Company.query.get(current_user.company_id)
    return render_template('corporate/dashboard.html', company=company)
```

**변경 후**:
```python
@corporate_bp.route('/dashboard')
@login_required
def dashboard():
    company = Company.query.get(current_user.company_id)
    return render_template('dashboard/base_dashboard.html',
        account_type='corporate',
        company=company
    )
```

#### 2.3 테스트 체크리스트

- [ ] 개인 계정 대시보드 표시 확인
- [ ] 법인 계정 대시보드 표시 확인
- [ ] 통계 카드 정상 표시
- [ ] 빠른 메뉴 링크 동작 확인

### Sprint 3: 사이드바 통합 (Phase 3)

#### 3.1 통합 사이드바 생성

**새 파일**: `app/templates/components/navigation/_sidebar_unified.html`

```jinja2
{# 통합 사이드바 - account_type과 role 기반 동적 메뉴 #}

{# 대시보드 섹션 (공통) #}
<div class="nav-section">
    <h2 class="nav-section-title">대시보드</h2>
    {% if current_user.account_type == 'personal' %}
    <a href="{{ url_for('personal.dashboard') }}" class="nav-item">
        <i class="fas fa-tachometer-alt"></i>
        <span>대시보드</span>
    </a>
    {% elif current_user.role == 'employee' %}
    <a href="{{ url_for('employees.employee_detail', employee_id=current_user.employee_id, view='basic') }}" class="nav-item">
        <i class="fas fa-id-card"></i>
        <span>내 인사카드</span>
    </a>
    {% else %}
    <a href="{{ url_for('main.index') }}" class="nav-item">
        <i class="fas fa-tachometer-alt"></i>
        <span>직원 현황</span>
    </a>
    {% endif %}
</div>

{# 내 정보 섹션 (개인/직원) #}
{% if current_user.account_type == 'personal' %}
<div class="nav-section">
    <h2 class="nav-section-title">내 정보</h2>
    <a href="{{ url_for('personal.profile') }}" class="nav-item">
        <i class="fas fa-user"></i>
        <span>프로필</span>
    </a>
    <a href="{{ url_for('personal.profile_edit') }}" class="nav-item">
        <i class="fas fa-user-edit"></i>
        <span>프로필 수정</span>
    </a>
</div>
{% endif %}

{# 직원 관리 섹션 (법인 관리자) #}
{% if current_user.account_type == 'corporate' and current_user.is_admin %}
<div class="nav-section">
    <h2 class="nav-section-title">직원 관리</h2>
    <a href="{{ url_for('employees.employee_list') }}" class="nav-item">
        <i class="fas fa-users"></i>
        <span>직원 목록</span>
    </a>
    <a href="{{ url_for('employees.employee_new') }}" class="nav-item">
        <i class="fas fa-user-plus"></i>
        <span>직원 등록</span>
    </a>
</div>
{% endif %}

{# 계약 관리 섹션 (공통) #}
<div class="nav-section">
    <h2 class="nav-section-title">계약 관리</h2>
    {% if current_user.account_type == 'personal' %}
    <a href="{{ url_for('contracts.my_contracts') }}" class="nav-item">
        <i class="fas fa-file-contract"></i>
        <span>내 계약</span>
    </a>
    <a href="{{ url_for('contracts.pending_contracts') }}" class="nav-item">
        <i class="fas fa-clock"></i>
        <span>대기 중인 요청</span>
    </a>
    {% elif current_user.account_type == 'corporate' %}
    <a href="{{ url_for('contracts.company_contracts') }}" class="nav-item">
        <i class="fas fa-file-contract"></i>
        <span>계약 목록</span>
    </a>
    <a href="{{ url_for('contracts.request_contract') }}" class="nav-item">
        <i class="fas fa-paper-plane"></i>
        <span>계약 요청</span>
    </a>
    {% endif %}
</div>

{# 법인 관리 섹션 (법인 관리자) #}
{% if current_user.account_type == 'corporate' and current_user.is_admin %}
<div class="nav-section">
    <h2 class="nav-section-title">법인 관리</h2>
    <a href="{{ url_for('corporate.dashboard') }}" class="nav-item">
        <i class="fas fa-building"></i>
        <span>법인 대시보드</span>
    </a>
    <a href="{{ url_for('profile.view') }}" class="nav-item">
        <i class="fas fa-user-tie"></i>
        <span>관리자 프로필</span>
    </a>
    <a href="{{ url_for('corporate.settings') }}" class="nav-item">
        <i class="fas fa-cog"></i>
        <span>법인 설정</span>
    </a>
    <a href="{{ url_for('corporate.users') }}" class="nav-item">
        <i class="fas fa-users-cog"></i>
        <span>사용자 관리</span>
    </a>
</div>
{% endif %}

{# 계정 관리 섹션 (직원) #}
{% if current_user.role == 'employee' %}
<div class="nav-section">
    <h2 class="nav-section-title">계정관리</h2>
    <a href="{{ url_for('auth.change_password') }}" class="nav-item">
        <i class="fas fa-key"></i>
        <span>계정정보</span>
    </a>
</div>
{% endif %}
```

#### 3.2 base.html 수정

**현재 상태** (109-115줄):
```jinja2
{% if current_user and current_user.account_type == 'personal' %}
    {% include 'components/navigation/_sidebar_personal.html' %}
{% elif current_user and current_user.role == 'employee' and current_user.employee_id %}
    {% include 'components/navigation/_sidebar_employee.html' %}
{% else %}
    {% include 'components/navigation/_sidebar_corporate.html' %}
{% endif %}
```

**변경 후**:
```jinja2
{% include 'components/navigation/_sidebar_unified.html' %}
```

### Sprint 4: 정리 (Phase 4)

#### 4.1 레거시 템플릿 처리

다음 파일들을 deprecated 처리:
- `app/templates/personal/profile.html`
- `app/templates/personal/dashboard.html`
- `app/templates/corporate/dashboard.html`

처리 방법:
1. 파일 상단에 deprecated 주석 추가
2. 3개월 후 삭제 예정 표시
3. 또는 즉시 삭제 후 Git 히스토리로 복원 가능

#### 4.2 불필요한 사이드바 정리

통합 완료 후:
- `_sidebar_personal.html` - deprecated
- `_sidebar_employee.html` - deprecated
- `_sidebar_corporate.html` - deprecated (단, AI 테스트 섹션 검토 필요)

## 롤백 계획

각 Sprint별 문제 발생 시:
1. Git revert로 이전 커밋 복원
2. 기존 템플릿 파일 유지했으므로 빠른 복구 가능

## 완료 기준

- [ ] 모든 계정 유형에서 프로필 정상 표시
- [ ] 모든 계정 유형에서 대시보드 정상 표시
- [ ] 사이드바 메뉴 정상 동작
- [ ] 기존 기능 회귀 없음
- [ ] 코드 중복 50% 이상 감소

## 참고 문서

- `claudedocs/workflow_14/template_integration_analysis.md`
- `app/adapters/profile_adapter.py`
- `app/blueprints/profile/routes.py`
