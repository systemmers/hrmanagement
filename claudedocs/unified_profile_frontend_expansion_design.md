# 통합프로필 프론트엔드 확장 설계

## 1. 개요

### 1.1 목적
HRM 시스템의 통합프로필 템플릿을 확장하여 3가지 계정 유형(법인직원, 법인관리자, 개인)을 단일 템플릿으로 지원

### 1.2 현재 상황 분석

#### 기존 구조
```
app/templates/
├── profile/
│   ├── unified_profile.html          # 법인 직원 전용 (is_corporate=True)
│   └── partials/
│       ├── _header_unified.html
│       ├── _section_nav_unified.html
│       └── sections/
│           ├── _basic_info.html      # 공통
│           ├── _organization_info.html  # 법인 전용
│           ├── _contract_info.html      # 법인 전용
│           ├── _salary_info.html        # 법인 전용
│           ├── _benefit_info.html       # 법인 전용
│           ├── _insurance_info.html     # 법인 전용
│           ├── _education_info.html     # 공통
│           ├── _career_info.html        # 공통
│           ├── _certificate_info.html   # 공통
│           ├── _language_info.html      # 공통
│           ├── _military_info.html      # 공통
│           ├── _employment_contract.html # 법인 전용
│           ├── _personnel_movement.html  # 법인 전용
│           └── _attendance_assets.html   # 법인 전용
└── personal/
    └── profile.html                  # 개인 계정 전용 (별도 구조)
```

#### 문제점
1. **법인 관리자 프로필 UI 부재**: 관리자용 프로필 페이지가 없음
2. **개인 계정 분리**: personal/profile.html이 완전히 다른 구조로 존재
3. **계정 유형별 UI 차별화 부족**: is_corporate 플래그만으로 구분, 관리자 구분 불가

### 1.3 설계 목표
1. **단일 템플릿 통합**: unified_profile.html로 3가지 계정 유형 지원
2. **유연한 섹션 렌더링**: account_type별 조건부 섹션 표시
3. **일관된 UI/UX**: 디자인 시스템 기반 통일된 사용자 경험
4. **확장 가능한 구조**: 향후 계정 유형 추가 용이

---

## 2. 아키텍처 설계

### 2.1 계정 유형 정의 (account_type)

```python
# 백엔드 모델 정의 예시
class AccountType:
    CORPORATE_EMPLOYEE = 'corporate_employee'  # 법인 직원
    CORPORATE_ADMIN = 'corporate_admin'        # 법인 관리자
    PERSONAL = 'personal'                      # 개인 계정
```

### 2.2 템플릿 구조 확장

#### 2.2.1 통합 템플릿 (unified_profile.html)

```jinja2
{% extends 'base.html' %}

{% block title %}
    {% if account_type == 'corporate_admin' %}
        관리자 프로필 - {{ profile_name }}
    {% elif account_type == 'corporate_employee' %}
        인사카드 - {{ profile_name }}
    {% else %}
        프로필 - {{ profile_name }}
    {% endif %}
{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/pages/profile.css') }}">
{% endblock %}

{% block content %}
<div class="profile-page" data-account-type="{{ account_type }}">
    {# 사이드 네비게이션 #}
    {% include 'profile/partials/_section_nav_unified.html' %}

    {# 메인 콘텐츠 영역 #}
    <main class="profile-main">
        {# 헤더 영역 #}
        {% include 'profile/partials/_header_unified.html' %}

        <div class="profile-content">
            {# 1. 공통 섹션: 기본 정보 (모든 계정 유형) #}
            {% include 'profile/partials/sections/_basic_info.html' %}

            {# 2. 법인 직원 전용 섹션 #}
            {% if account_type == 'corporate_employee' %}
                {% include 'profile/partials/sections/_organization_info.html' %}
                {% include 'profile/partials/sections/_contract_info.html' %}
                {% include 'profile/partials/sections/_salary_info.html' %}
                {% include 'profile/partials/sections/_benefit_info.html' %}
                {% include 'profile/partials/sections/_insurance_info.html' %}
            {% endif %}

            {# 3. 법인 관리자 전용 섹션 #}
            {% if account_type == 'corporate_admin' %}
                {% include 'profile/partials/sections/_admin_company_info.html' %}
                {% include 'profile/partials/sections/_admin_settings.html' %}
            {% endif %}

            {# 4. 공통 섹션: 이력 및 경력 (법인 직원, 개인) #}
            {% if account_type in ['corporate_employee', 'personal'] %}
                {% include 'profile/partials/sections/_education_info.html' %}
                {% include 'profile/partials/sections/_career_info.html' %}
                {% include 'profile/partials/sections/_certificate_info.html' %}
                {% include 'profile/partials/sections/_language_info.html' %}
                {% include 'profile/partials/sections/_military_info.html' %}
            {% endif %}

            {# 5. 법인 직원 전용: 인사기록 #}
            {% if account_type == 'corporate_employee' %}
                {% include 'profile/partials/sections/_employment_contract.html' %}
                {% include 'profile/partials/sections/_personnel_movement.html' %}
                {% include 'profile/partials/sections/_attendance_assets.html' %}
            {% endif %}
        </div>
    </main>
</div>
{% endblock %}

{% block extra_js %}
<script src="{{ url_for('static', filename='js/pages/profile/profile-navigation.js') }}"></script>
<script>
document.addEventListener('DOMContentLoaded', function() {
    if (window.ProfileNavigation) {
        window.ProfileNavigation.initProfileNavigation();
    }
});
</script>
{% endblock %}
```

#### 2.2.2 섹션 네비게이션 (_section_nav_unified.html)

```jinja2
<aside class="section-nav" id="sectionNav">
    <div class="section-nav-header">
        <div class="section-nav-title">
            {% if account_type == 'corporate_admin' %}
                관리자 프로필
            {% elif account_type == 'corporate_employee' %}
                인사카드
            {% else %}
                프로필
            {% endif %}
        </div>
        <div class="section-nav-subtitle">{{ profile_name }}</div>
    </div>

    <nav class="section-nav-menu">
        {# 기본정보 그룹 #}
        <div class="section-nav-group">
            <div class="section-nav-group-title">기본정보</div>
            <a href="#basic-info" class="section-nav-item active">
                <i class="fas fa-user"></i>
                <span>개인 기본정보</span>
            </a>

            {# 법인 직원 전용 #}
            {% if account_type == 'corporate_employee' %}
            <a href="#organization-info" class="section-nav-item">
                <i class="fas fa-building"></i>
                <span>소속정보</span>
            </a>
            <a href="#contract-info" class="section-nav-item">
                <i class="fas fa-file-contract"></i>
                <span>계약정보</span>
            </a>
            <a href="#salary-info" class="section-nav-item">
                <i class="fas fa-won-sign"></i>
                <span>급여정보</span>
            </a>
            <a href="#benefit-info" class="section-nav-item">
                <i class="fas fa-umbrella-beach"></i>
                <span>연차 및 복리후생</span>
            </a>
            <a href="#insurance-info" class="section-nav-item">
                <i class="fas fa-shield-alt"></i>
                <span>4대보험</span>
            </a>
            {% endif %}

            {# 법인 관리자 전용 #}
            {% if account_type == 'corporate_admin' %}
            <a href="#admin-company-info" class="section-nav-item">
                <i class="fas fa-building"></i>
                <span>회사정보</span>
            </a>
            <a href="#admin-settings" class="section-nav-item">
                <i class="fas fa-cog"></i>
                <span>계정 설정</span>
            </a>
            {% endif %}
        </div>

        {# 이력 및 경력 그룹 (법인 직원, 개인) #}
        {% if account_type in ['corporate_employee', 'personal'] %}
        <div class="section-nav-group">
            <div class="section-nav-group-title">이력 및 경력</div>
            <a href="#education-info" class="section-nav-item">
                <i class="fas fa-graduation-cap"></i>
                <span>학력정보</span>
            </a>
            <a href="#career-info" class="section-nav-item">
                <i class="fas fa-briefcase"></i>
                <span>경력정보</span>
            </a>
            <a href="#certificate-info" class="section-nav-item">
                <i class="fas fa-certificate"></i>
                <span>자격증 및 면허</span>
            </a>
            <a href="#language-info" class="section-nav-item">
                <i class="fas fa-language"></i>
                <span>언어능력</span>
            </a>
            <a href="#military-info" class="section-nav-item">
                <i class="fas fa-medal"></i>
                <span>병역/프로젝트/수상</span>
            </a>
        </div>
        {% endif %}

        {# 인사기록 그룹 (법인 직원 전용) #}
        {% if account_type == 'corporate_employee' %}
        <div class="section-nav-group">
            <div class="section-nav-group-title">인사기록</div>
            <a href="#employment-contract" class="section-nav-item">
                <i class="fas fa-file-signature"></i>
                <span>근로계약 및 연봉</span>
            </a>
            <a href="#personnel-movement" class="section-nav-item">
                <i class="fas fa-arrow-up"></i>
                <span>인사이동 및 고과</span>
            </a>
            <a href="#attendance-assets" class="section-nav-item">
                <i class="fas fa-calendar-check"></i>
                <span>근태 및 비품</span>
            </a>
        </div>
        {% endif %}
    </nav>
</aside>
```

#### 2.2.3 프로필 헤더 (_header_unified.html)

```jinja2
<header class="profile-header">
    <div class="profile-header-content">
        {# 프로필 사진 #}
        <div class="profile-avatar">
            {% if basic_info.photo %}
            <img src="{{ url_for('static', filename='images/face/' ~ basic_info.photo) }}"
                 alt="{{ basic_info.name }}">
            {% else %}
            <div class="profile-avatar-placeholder">
                <i class="fas fa-user"></i>
            </div>
            {% endif %}
        </div>

        {# 프로필 정보 #}
        <div class="profile-info">
            <h1 class="profile-name">
                {{ basic_info.name }}
                {% if basic_info.english_name %}
                <span class="profile-name-en">({{ basic_info.english_name }})</span>
                {% endif %}
            </h1>

            {# 법인 직원 메타정보 #}
            {% if account_type == 'corporate_employee' and organization_info %}
            <div class="profile-position">
                {{ organization_info.department or '' }}
                {% if organization_info.department and organization_info.position %} / {% endif %}
                {{ organization_info.position or '' }}
            </div>
            <div class="profile-meta">
                {% if basic_info.employee_number %}
                <span class="profile-meta-item">
                    <i class="fas fa-id-badge"></i>
                    {{ basic_info.employee_number }}
                </span>
                {% endif %}
                {% if organization_info.hire_date %}
                <span class="profile-meta-item">
                    <i class="fas fa-calendar"></i>
                    입사일: {{ organization_info.hire_date }}
                </span>
                {% endif %}
            </div>
            {% endif %}

            {# 법인 관리자 메타정보 #}
            {% if account_type == 'corporate_admin' %}
            <div class="profile-role">
                <span class="profile-badge profile-badge--admin">
                    <i class="fas fa-shield-alt"></i>
                    관리자
                </span>
            </div>
            <div class="profile-meta">
                {% if admin_info.company_name %}
                <span class="profile-meta-item">
                    <i class="fas fa-building"></i>
                    {{ admin_info.company_name }}
                </span>
                {% endif %}
                {% if basic_info.email %}
                <span class="profile-meta-item">
                    <i class="fas fa-envelope"></i>
                    {{ basic_info.email }}
                </span>
                {% endif %}
            </div>
            {% endif %}

            {# 개인 계정 메타정보 #}
            {% if account_type == 'personal' %}
            <div class="profile-contact">
                {% if basic_info.email %}
                <span class="profile-contact-item">
                    <i class="fas fa-envelope"></i>
                    {{ basic_info.email }}
                </span>
                {% endif %}
                {% if basic_info.mobile_phone %}
                <span class="profile-contact-item">
                    <i class="fas fa-phone"></i>
                    {{ basic_info.mobile_phone }}
                </span>
                {% endif %}
            </div>
            {% endif %}
        </div>

        {# 액션 버튼 영역 #}
        <div class="profile-actions">
            {% if account_type == 'corporate_employee' %}
            <button type="button" class="btn btn-outline" onclick="window.print()">
                <i class="fas fa-print"></i>
                인쇄
            </button>
            {% endif %}

            {% if account_type == 'corporate_admin' %}
            <a href="{{ url_for('corporate.settings') }}" class="btn btn-outline">
                <i class="fas fa-cog"></i>
                설정
            </a>
            {% endif %}

            {% if account_type == 'personal' %}
            <a href="{{ url_for('personal.profile_edit') }}" class="btn btn-primary">
                <i class="fas fa-edit"></i>
                수정
            </a>
            {% endif %}
        </div>
    </div>
</header>
```

---

## 3. 신규 섹션 컴포넌트 설계

### 3.1 법인 관리자 전용 섹션

#### 3.1.1 회사정보 (_admin_company_info.html)

```jinja2
{#
    회사 정보 섹션 (법인 관리자 전용)
    admin_info: 관리자 정보 딕셔너리
#}
<section class="profile-section" id="admin-company-info">
    <div class="section-header">
        <h2 class="section-title">
            <i class="fas fa-building"></i>
            회사정보
        </h2>
    </div>

    <div class="section-content">
        {% if admin_info %}
        <div class="info-grid">
            <div class="info-group">
                <label class="info-label">회사명</label>
                <div class="info-value">{{ admin_info.company_name or '-' }}</div>
            </div>

            <div class="info-group">
                <label class="info-label">사업자등록번호</label>
                <div class="info-value">{{ admin_info.business_number or '-' }}</div>
            </div>

            <div class="info-group">
                <label class="info-label">대표자명</label>
                <div class="info-value">{{ admin_info.ceo_name or '-' }}</div>
            </div>

            <div class="info-group">
                <label class="info-label">업종</label>
                <div class="info-value">{{ admin_info.industry or '-' }}</div>
            </div>

            <div class="info-group info-group--full">
                <label class="info-label">회사 주소</label>
                <div class="info-value">
                    {% if admin_info.postal_code %}
                    <span class="info-postal">({{ admin_info.postal_code }})</span>
                    {% endif %}
                    {{ admin_info.address or '-' }}
                    {% if admin_info.detailed_address %}
                    {{ admin_info.detailed_address }}
                    {% endif %}
                </div>
            </div>

            <div class="info-group">
                <label class="info-label">대표 전화</label>
                <div class="info-value">{{ admin_info.company_phone or '-' }}</div>
            </div>

            <div class="info-group">
                <label class="info-label">팩스</label>
                <div class="info-value">{{ admin_info.fax or '-' }}</div>
            </div>

            <div class="info-group">
                <label class="info-label">직원 수</label>
                <div class="info-value info-value--highlight">{{ admin_info.employee_count or 0 }}명</div>
            </div>

            <div class="info-group">
                <label class="info-label">설립일</label>
                <div class="info-value">{{ admin_info.established_date or '-' }}</div>
            </div>
        </div>
        {% else %}
        <div class="empty-state">
            <i class="fas fa-building"></i>
            <p>회사 정보가 없습니다.</p>
        </div>
        {% endif %}
    </div>
</section>
```

#### 3.1.2 계정 설정 (_admin_settings.html)

```jinja2
{#
    계정 설정 섹션 (법인 관리자 전용)
    admin_info: 관리자 정보 딕셔너리
#}
<section class="profile-section" id="admin-settings">
    <div class="section-header">
        <h2 class="section-title">
            <i class="fas fa-cog"></i>
            계정 설정
        </h2>
    </div>

    <div class="section-content">
        <div class="subsection">
            <h3 class="subsection-title">
                <i class="fas fa-user-shield"></i>
                권한 정보
            </h3>
            <div class="info-grid">
                <div class="info-group">
                    <label class="info-label">계정 유형</label>
                    <div class="info-value">
                        <span class="status-badge status-badge--info">관리자</span>
                    </div>
                </div>

                <div class="info-group">
                    <label class="info-label">권한 레벨</label>
                    <div class="info-value">{{ admin_info.permission_level or '-' }}</div>
                </div>

                <div class="info-group">
                    <label class="info-label">가입일</label>
                    <div class="info-value">{{ admin_info.created_at or '-' }}</div>
                </div>

                <div class="info-group">
                    <label class="info-label">마지막 로그인</label>
                    <div class="info-value">{{ admin_info.last_login or '-' }}</div>
                </div>
            </div>
        </div>

        <div class="subsection">
            <h3 class="subsection-title">
                <i class="fas fa-envelope"></i>
                알림 설정
            </h3>
            <div class="info-grid">
                <div class="info-group">
                    <label class="info-label">이메일 알림</label>
                    <div class="info-value">
                        <span class="status-badge {{ 'status-badge--active' if admin_info.email_notification else 'status-badge--inactive' }}">
                            {{ '활성' if admin_info.email_notification else '비활성' }}
                        </span>
                    </div>
                </div>

                <div class="info-group">
                    <label class="info-label">시스템 알림</label>
                    <div class="info-value">
                        <span class="status-badge {{ 'status-badge--active' if admin_info.system_notification else 'status-badge--inactive' }}">
                            {{ '활성' if admin_info.system_notification else '비활성' }}
                        </span>
                    </div>
                </div>
            </div>
        </div>

        <div class="subsection">
            <h3 class="subsection-title">
                <i class="fas fa-tools"></i>
                관리 기능
            </h3>
            <div class="quick-actions">
                <a href="{{ url_for('corporate.settings') }}" class="quick-action-card">
                    <i class="fas fa-building"></i>
                    <span>회사 설정</span>
                </a>
                <a href="{{ url_for('corporate.users') }}" class="quick-action-card">
                    <i class="fas fa-users"></i>
                    <span>직원 관리</span>
                </a>
                <a href="{{ url_for('admin.dashboard') }}" class="quick-action-card">
                    <i class="fas fa-chart-line"></i>
                    <span>관리 대시보드</span>
                </a>
            </div>
        </div>
    </div>
</section>
```

### 3.2 개인 계정 통합 UI

기존 `personal/profile.html`의 내용을 `unified_profile.html`로 통합하기 위한 마이그레이션 가이드:

#### 3.2.1 마이그레이션 체크리스트
- [x] 기본 정보 섹션: 이미 `_basic_info.html`로 통합됨
- [x] 학력/경력/자격증/언어: 이미 공통 섹션으로 존재
- [ ] personal/profile.html의 스타일 클래스 매핑 필요
- [ ] 개인 계정 특화 액션 버튼 추가

#### 3.2.2 스타일 클래스 매핑

기존 `personal/profile.html`의 클래스를 `unified_profile.html` 디자인 시스템에 매핑:

```css
/* personal/profile.html (기존) → unified_profile.html (신규) */
.profile-container → .profile-content
.profile-section → .profile-section (동일)
.profile-card → .section-content
.info-grid → .info-grid (동일)
.info-item → .info-group
.info-label → .info-label (동일)
.info-value → .info-value (동일)
.history-list → .timeline
.history-item → .timeline-item
.count-badge → .section-title 내 badge
```

---

## 4. CSS/JS 확장 설계

### 4.1 CSS 테마 변수 확장

**파일**: `app/static/css/pages/profile.css`

```css
/* ----------------------------------------
   계정 유형별 테마 변수
   ---------------------------------------- */

/* 법인 직원 테마 (기본) */
[data-account-type="corporate_employee"] {
    --profile-primary: var(--color-blue-600);
    --profile-primary-hover: var(--color-blue-700);
    --profile-primary-light: var(--color-blue-50);
    --profile-accent: var(--color-primary-500);
    --profile-gradient: var(--gradient-blue);
}

/* 법인 관리자 테마 */
[data-account-type="corporate_admin"] {
    --profile-primary: #7c3aed;  /* purple-600 */
    --profile-primary-hover: #6d28d9;  /* purple-700 */
    --profile-primary-light: #f5f3ff;  /* purple-50 */
    --profile-accent: #8b5cf6;  /* purple-500 */
    --profile-gradient: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%);
}

/* 개인 계정 테마 */
[data-account-type="personal"] {
    --profile-primary: #059669;  /* emerald-600 */
    --profile-primary-hover: #047857;  /* emerald-700 */
    --profile-primary-light: #ecfdf5;  /* emerald-50 */
    --profile-accent: #10b981;  /* emerald-500 */
    --profile-gradient: linear-gradient(135deg, #059669 0%, #047857 100%);
}
```

### 4.2 관리자 프로필 전용 스타일

```css
/* ----------------------------------------
   관리자 프로필 전용 스타일
   ---------------------------------------- */

/* 관리자 배지 */
.profile-badge--admin {
    background: rgba(124, 58, 237, 0.2);
    color: #7c3aed;
    font-weight: 600;
    padding: var(--space-2) var(--space-4);
    border-radius: var(--radius-md);
    display: inline-flex;
    align-items: center;
    gap: var(--space-2);
}

/* 빠른 액션 카드 */
.quick-actions {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: var(--space-4);
    margin-top: var(--space-4);
}

.quick-action-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-5);
    background: var(--color-gray-25);
    border: 1px solid var(--color-gray-200);
    border-radius: var(--radius-lg);
    text-decoration: none;
    color: var(--color-gray-700);
    transition: all var(--transition-normal);
}

.quick-action-card:hover {
    background: var(--profile-primary-light);
    border-color: var(--profile-primary);
    color: var(--profile-primary);
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
}

.quick-action-card i {
    font-size: var(--text-2xl);
    color: var(--profile-primary);
}

.quick-action-card span {
    font-size: var(--text-sm);
    font-weight: 600;
    text-align: center;
}

/* 관리자 통계 카드 */
.admin-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: var(--space-4);
    margin-bottom: var(--space-6);
}

.admin-stat-card {
    background: var(--color-pure-white);
    border: 1px solid var(--color-gray-200);
    border-radius: var(--radius-lg);
    padding: var(--space-4);
    display: flex;
    align-items: center;
    gap: var(--space-4);
}

.admin-stat-icon {
    width: 48px;
    height: 48px;
    border-radius: var(--radius-md);
    background: var(--profile-primary-light);
    color: var(--profile-primary);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: var(--text-xl);
    flex-shrink: 0;
}

.admin-stat-content {
    flex: 1;
}

.admin-stat-label {
    font-size: var(--text-sm);
    color: var(--color-gray-600);
    margin-bottom: var(--space-1);
}

.admin-stat-value {
    font-size: var(--text-2xl);
    font-weight: 700;
    color: var(--color-gray-900);
}
```

### 4.3 JavaScript 모듈 확장

**파일**: `app/static/js/pages/profile/profile-navigation.js`

기존 코드는 유지하고, account_type별 동작 추가:

```javascript
/**
 * 프로필 네비게이션 초기화
 * @param {Object} options - 초기화 옵션
 */
export function initProfileNavigation(options = {}) {
    const {
        navSelector = '.section-nav-item',
        sectionSelector = '.profile-section',
        scrollOffset = 100
    } = options;

    const navItems = document.querySelectorAll(navSelector);
    const sections = document.querySelectorAll(sectionSelector);
    const accountType = document.querySelector('.profile-page')?.dataset.accountType;

    if (navItems.length === 0 || sections.length === 0) {
        return;
    }

    // Account type별 특수 동작
    if (accountType === 'corporate_admin') {
        initAdminProfileFeatures();
    } else if (accountType === 'personal') {
        initPersonalProfileFeatures();
    }

    // 스크롤 시 활성 섹션 업데이트
    window.addEventListener('scroll', function() {
        updateActiveNav(navItems, sections, scrollOffset);
    });

    // 네비게이션 클릭 시 부드러운 스크롤
    navItems.forEach(item => {
        item.addEventListener('click', smoothScrollToSection);
    });

    // 초기 활성 상태 설정
    updateActiveNav(navItems, sections, scrollOffset);
}

/**
 * 관리자 프로필 전용 기능 초기화
 */
function initAdminProfileFeatures() {
    console.log('관리자 프로필 기능 초기화');
    // 관리자 통계 새로고침, 빠른 액션 버튼 이벤트 등
}

/**
 * 개인 계정 프로필 전용 기능 초기화
 */
function initPersonalProfileFeatures() {
    console.log('개인 계정 프로필 기능 초기화');
    // 프로필 수정 버튼 강조, 이력 추가 안내 등
}
```

---

## 5. 컴포넌트 재사용 전략

### 5.1 공통 컴포넌트 (모든 계정 유형)

- `_basic_info.html` - 개인 기본정보
- `_education_info.html` - 학력정보
- `_career_info.html` - 경력정보
- `_certificate_info.html` - 자격증 및 면허
- `_language_info.html` - 언어능력
- `_military_info.html` - 병역/프로젝트/수상

### 5.2 법인 직원 전용 컴포넌트

- `_organization_info.html` - 소속정보
- `_contract_info.html` - 계약정보
- `_salary_info.html` - 급여정보
- `_benefit_info.html` - 연차 및 복리후생
- `_insurance_info.html` - 4대보험
- `_employment_contract.html` - 근로계약 및 연봉
- `_personnel_movement.html` - 인사이동 및 고과
- `_attendance_assets.html` - 근태 및 비품

### 5.3 법인 관리자 전용 컴포넌트 (신규)

- `_admin_company_info.html` - 회사정보
- `_admin_settings.html` - 계정 설정

### 5.4 개인 계정 전용 컴포넌트

현재는 공통 컴포넌트로 충분하나, 향후 필요시:
- `_personal_portfolio.html` - 포트폴리오 (선택적)
- `_personal_preferences.html` - 개인 설정 (선택적)

---

## 6. 백엔드 라우팅 및 데이터 구조

### 6.1 라우팅 설계

```python
# app/routes/profile.py (예시)

from flask import Blueprint, render_template, session
from app.models import User, CorporateEmployee, CorporateAdmin, PersonalUser

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile')
def view_profile():
    user = get_current_user()
    account_type = determine_account_type(user)

    # 공통 데이터
    basic_info = get_basic_info(user)

    # 계정 유형별 데이터 준비
    context = {
        'account_type': account_type,
        'profile_name': basic_info.get('name'),
        'basic_info': basic_info,
    }

    if account_type == 'corporate_employee':
        context.update({
            'organization_info': get_organization_info(user),
            'contract_info': get_contract_info(user),
            'salary_info': get_salary_info(user),
            'benefit_info': get_benefit_info(user),
            'insurance_info': get_insurance_info(user),
            'education_info': get_education_info(user),
            'career_info': get_career_info(user),
            # ... 기타 정보
        })
    elif account_type == 'corporate_admin':
        context.update({
            'admin_info': get_admin_info(user),
        })
    elif account_type == 'personal':
        context.update({
            'education_info': get_education_info(user),
            'career_info': get_career_info(user),
            # ... 기타 이력 정보
        })

    return render_template('profile/unified_profile.html', **context)

def determine_account_type(user):
    """사용자 계정 유형 판별"""
    if isinstance(user, CorporateAdmin):
        return 'corporate_admin'
    elif isinstance(user, CorporateEmployee):
        return 'corporate_employee'
    elif isinstance(user, PersonalUser):
        return 'personal'
    else:
        raise ValueError('Unknown user type')
```

### 6.2 데이터 구조 예시

```python
# 법인 관리자 정보 딕셔너리 구조
admin_info = {
    'company_name': '테스트 주식회사',
    'business_number': '123-45-67890',
    'ceo_name': '홍길동',
    'industry': 'IT 서비스',
    'postal_code': '06234',
    'address': '서울특별시 강남구 테헤란로 123',
    'detailed_address': '4층',
    'company_phone': '02-1234-5678',
    'fax': '02-1234-5679',
    'employee_count': 50,
    'established_date': '2020-01-15',
    'permission_level': 'Super Admin',
    'created_at': '2020-01-15',
    'last_login': '2025-12-11 14:30:00',
    'email_notification': True,
    'system_notification': True,
}
```

---

## 7. 마이그레이션 가이드

### 7.1 단계별 마이그레이션 계획

#### Phase 1: 백엔드 준비
1. account_type 필드 추가 및 마이그레이션
2. 라우팅 통합 (기존 personal/profile → profile/unified_profile)
3. 데이터 준비 함수 작성 (get_admin_info 등)

#### Phase 2: 신규 컴포넌트 생성
1. `_admin_company_info.html` 작성
2. `_admin_settings.html` 작성
3. CSS 테마 변수 추가 (corporate_admin)

#### Phase 3: 템플릿 통합
1. `unified_profile.html` 확장 (account_type 조건 추가)
2. `_section_nav_unified.html` 확장
3. `_header_unified.html` 확장

#### Phase 4: 스타일 및 JS 확장
1. profile.css에 관리자 스타일 추가
2. profile-navigation.js 확장 (계정 유형별 동작)

#### Phase 5: 테스트 및 검증
1. 3가지 계정 유형별 프로필 페이지 렌더링 검증
2. 섹션 네비게이션 동작 테스트
3. 반응형 레이아웃 검증

#### Phase 6: 기존 템플릿 제거
1. `personal/profile.html` 제거
2. 라우팅 리다이렉트 설정 (기존 URL → 통합 URL)

### 7.2 기존 코드 영향 분석

**영향받는 파일**:
- `app/routes/personal.py` - 라우팅 변경
- `app/routes/profile.py` - 라우팅 통합
- `app/templates/personal/profile.html` - 제거 예정
- `app/templates/profile/unified_profile.html` - 확장
- `app/static/css/pages/profile.css` - 스타일 추가

**안전한 마이그레이션 전략**:
1. 기존 `personal/profile.html`을 유지하면서 `unified_profile.html` 확장
2. 신규 라우팅을 별도 URL로 먼저 배포 (예: `/profile/unified`)
3. 검증 완료 후 기존 URL을 새 템플릿으로 전환
4. 최종 안정화 후 구 템플릿 제거

---

## 8. 접근성 및 사용자 경험

### 8.1 WCAG 2.1 AA 준수

- **키보드 네비게이션**: 모든 섹션 네비게이션 항목은 Tab 키로 접근 가능
- **스크린 리더 지원**: 섹션 제목에 적절한 heading level 사용 (h2, h3)
- **색상 대비**: 텍스트와 배경 대비 4.5:1 이상 유지
- **포커스 인디케이터**: 키보드 포커스 시 명확한 시각적 피드백

### 8.2 반응형 디자인

- **모바일 네비게이션**: 1024px 이하에서 햄버거 메뉴로 전환
- **터치 타겟 크기**: 최소 44x44px 확보
- **그리드 레이아웃**: 화면 크기에 따라 자동 조정 (auto-fit, minmax)

### 8.3 성능 최적화

- **지연 로딩**: 이미지 lazy loading 적용
- **CSS 변수 활용**: 테마 변경 시 재계산 최소화
- **섹션별 렌더링**: 조건부 include로 불필요한 HTML 생성 방지

---

## 9. 테스트 시나리오

### 9.1 기능 테스트

| 계정 유형 | 테스트 항목 | 기대 결과 |
|-----------|-------------|-----------|
| 법인 직원 | 프로필 접근 | 인사카드 화면, 13개 섹션 표시 |
| 법인 직원 | 섹션 네비게이션 | 스크롤 시 active 상태 변경 |
| 법인 직원 | 인쇄 버튼 | 프린트 미리보기 표시 |
| 법인 관리자 | 프로필 접근 | 관리자 프로필 화면, 4개 섹션 표시 |
| 법인 관리자 | 회사정보 섹션 | 사업자등록번호, 직원 수 등 표시 |
| 법인 관리자 | 빠른 액션 | 회사 설정, 직원 관리 링크 동작 |
| 개인 계정 | 프로필 접근 | 프로필 화면, 6개 섹션 표시 |
| 개인 계정 | 수정 버튼 | 프로필 수정 페이지로 이동 |
| 개인 계정 | 이력 섹션 | 학력/경력/자격증 표시 |

### 9.2 UI/UX 테스트

- [ ] 계정 유형별 테마 색상 적용 (법인: 파랑, 관리자: 보라, 개인: 초록)
- [ ] 헤더 정보 계정별 차별화 (직원: 사번+입사일, 관리자: 회사명, 개인: 연락처)
- [ ] 반응형 레이아웃 (데스크톱, 태블릿, 모바일)
- [ ] 키보드 네비게이션 (Tab, Enter)
- [ ] 스크린 리더 호환성 (NVDA, JAWS)

### 9.3 성능 테스트

- [ ] 페이지 로드 시간 < 2초 (3G 네트워크)
- [ ] First Contentful Paint < 1.5초
- [ ] Lighthouse 점수 > 90 (Performance, Accessibility)

---

## 10. 향후 확장 가능성

### 10.1 추가 계정 유형 지원

새로운 계정 유형 추가 시 필요한 작업:

1. **백엔드**: account_type enum 확장
2. **템플릿**: unified_profile.html에 조건 블록 추가
3. **섹션**: 신규 섹션 컴포넌트 작성
4. **CSS**: 테마 변수 추가
5. **JS**: 계정 유형별 동작 추가

예시: `contractor` (계약직 전문가) 계정 유형 추가

```jinja2
{% if account_type == 'contractor' %}
    {% include 'profile/partials/sections/_contractor_projects.html' %}
    {% include 'profile/partials/sections/_contractor_rates.html' %}
{% endif %}
```

### 10.2 다국어 지원 준비

- **i18n 라이브러리 통합**: Flask-Babel
- **섹션 제목 변수화**: `{{ _('기본정보') }}`
- **데이터 포맷팅**: 날짜, 통화 형식 로케일별 처리

### 10.3 프로필 커스터마이징

사용자가 프로필 섹션 순서/표시 여부를 직접 설정:

```python
# 사용자 설정 저장 예시
user_profile_settings = {
    'visible_sections': ['basic-info', 'education-info', 'career-info'],
    'section_order': ['basic-info', 'career-info', 'education-info'],
}
```

---

## 11. 구현 체크리스트

### 11.1 백엔드 작업
- [ ] `account_type` 필드 추가 (User 모델)
- [ ] `determine_account_type()` 함수 구현
- [ ] `get_admin_info()` 함수 구현
- [ ] 라우팅 통합 (`profile_bp` 확장)
- [ ] 데이터 마이그레이션 스크립트 작성

### 11.2 프론트엔드 작업
- [ ] `unified_profile.html` 확장 (account_type 조건)
- [ ] `_section_nav_unified.html` 확장
- [ ] `_header_unified.html` 확장
- [ ] `_admin_company_info.html` 작성
- [ ] `_admin_settings.html` 작성
- [ ] `profile.css` 테마 변수 추가 (corporate_admin)
- [ ] 관리자 전용 스타일 추가 (.quick-actions, .admin-stats)
- [ ] `profile-navigation.js` 확장

### 11.3 테스트 작업
- [ ] 법인 직원 프로필 렌더링 테스트
- [ ] 법인 관리자 프로필 렌더링 테스트
- [ ] 개인 계정 프로필 렌더링 테스트
- [ ] 섹션 네비게이션 동작 테스트
- [ ] 반응형 레이아웃 테스트 (모바일/태블릿/데스크톱)
- [ ] 접근성 테스트 (키보드, 스크린 리더)
- [ ] 성능 테스트 (Lighthouse)

### 11.4 문서화 작업
- [ ] API 문서 업데이트 (profile 엔드포인트)
- [ ] 프론트엔드 컴포넌트 문서 작성
- [ ] 사용자 가이드 작성 (계정 유형별)

---

## 12. 참고 자료

### 12.1 기존 파일 위치
- **통합 템플릿**: `app/templates/profile/unified_profile.html`
- **개인 템플릿**: `app/templates/personal/profile.html`
- **섹션 컴포넌트**: `app/templates/profile/partials/sections/`
- **프로필 CSS**: `app/static/css/pages/profile.css`
- **프로필 JS**: `app/static/js/pages/profile/`

### 12.2 관련 디자인 시스템
- **테마 변수**: `app/static/css/variables.css`
- **컴포넌트**: `app/static/css/components/`
- **유틸리티**: `app/static/css/utilities.css`

### 12.3 외부 라이브러리
- **FontAwesome**: 아이콘 시스템
- **Jinja2**: 템플릿 엔진
- **Flask**: 백엔드 프레임워크

---

## 13. 결론

이 설계는 통합프로필 템플릿을 3가지 계정 유형(법인직원, 법인관리자, 개인)으로 확장하여 단일 템플릿으로 관리할 수 있는 아키텍처를 제공합니다.

**핵심 설계 원칙**:
1. **단일 책임 원칙**: 각 섹션 컴포넌트는 하나의 정보 영역만 담당
2. **조건부 렌더링**: account_type 기반 동적 섹션 표시
3. **테마 시스템**: CSS 변수로 계정 유형별 브랜딩
4. **접근성 우선**: WCAG 2.1 AA 준수
5. **확장 가능성**: 새로운 계정 유형 추가 용이

**기대 효과**:
- 템플릿 관리 복잡도 감소 (3개 → 1개)
- 일관된 사용자 경험 제공
- 유지보수 비용 절감
- 향후 확장성 확보

**다음 단계**:
1. 백엔드 account_type 필드 추가
2. 관리자 섹션 컴포넌트 구현
3. 템플릿 통합 및 테스트
4. 점진적 마이그레이션 (기존 코드 유지하며 전환)
