# 인터페이스 통합 설계 문서

## 개요
- **문서 목적**: 법인 개인계정과 일반 개인계정 인터페이스 통합을 위한 상세 설계
- **기반 문서**:
  - `account_interface_analysis.md` - 인터페이스 비교 분석
  - `interface_integration_review.md` - 다중 전문가 검토 보고서
- **작성일**: 2025-12-10

---

## 1. 아키텍처 설계

### 1.1 핵심 패턴: Adapter Pattern

데이터 모델 차이를 추상화하기 위한 어댑터 패턴 적용

```
┌─────────────────────────────────────────────────────────────┐
│                    ProfileAdapter (ABC)                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ + get_basic_info() -> Dict                          │   │
│  │ + get_organization_info() -> Optional[Dict]         │   │
│  │ + get_education_list() -> List                      │   │
│  │ + get_career_list() -> List                         │   │
│  │ + is_corporate() -> bool                            │   │
│  │ + get_available_sections() -> List[str]             │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
              ▲                           ▲
              │                           │
┌─────────────┴─────────────┐ ┌─────────────┴─────────────┐
│ EmployeeProfileAdapter    │ │ PersonalProfileAdapter    │
│ (법인 직원용)              │ │ (일반 개인용)              │
│                           │ │                           │
│ - employee: Employee      │ │ - profile: PersonalProfile│
│ - is_corporate() = True   │ │ - is_corporate() = False  │
└───────────────────────────┘ └───────────────────────────┘
```

### 1.2 파일 구조

```
app/
├── adapters/
│   ├── __init__.py
│   └── profile_adapter.py          # ProfileAdapter 구현
├── blueprints/
│   └── profile/
│       ├── __init__.py
│       ├── routes.py               # 통합 라우트
│       └── decorators.py           # @unified_profile_required
├── context_processors/
│   └── profile_context.py          # inject_profile_context
└── templates/
    └── profile/
        ├── unified_profile.html    # 통합 프로필 메인
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

---

## 2. 구현 상세 설계

### 2.1 ProfileAdapter 인터페이스

**파일**: `app/adapters/profile_adapter.py`

```python
"""
Profile Adapter - 법인/개인 계정 데이터 모델 통합 어댑터

데이터 모델 차이를 추상화하여 템플릿에서 일관된 인터페이스 제공
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class ProfileAdapter(ABC):
    """프로필 데이터 접근을 위한 추상 어댑터"""

    @abstractmethod
    def get_basic_info(self) -> Dict[str, Any]:
        """기본 정보 (이름, 연락처 등) 반환"""
        pass

    @abstractmethod
    def get_organization_info(self) -> Optional[Dict[str, Any]]:
        """소속 정보 반환 (법인 전용, 개인은 None)"""
        pass

    @abstractmethod
    def get_contract_info(self) -> Optional[Dict[str, Any]]:
        """계약 정보 반환 (법인 전용)"""
        pass

    @abstractmethod
    def get_salary_info(self) -> Optional[Dict[str, Any]]:
        """급여 정보 반환 (법인 전용)"""
        pass

    @abstractmethod
    def get_benefit_info(self) -> Optional[Dict[str, Any]]:
        """복리후생 정보 반환 (법인 전용)"""
        pass

    @abstractmethod
    def get_insurance_info(self) -> Optional[Dict[str, Any]]:
        """4대보험 정보 반환 (법인 전용)"""
        pass

    @abstractmethod
    def get_education_list(self) -> List[Dict[str, Any]]:
        """학력 정보 목록 반환"""
        pass

    @abstractmethod
    def get_career_list(self) -> List[Dict[str, Any]]:
        """경력 정보 목록 반환"""
        pass

    @abstractmethod
    def get_certificate_list(self) -> List[Dict[str, Any]]:
        """자격증 목록 반환"""
        pass

    @abstractmethod
    def get_language_list(self) -> List[Dict[str, Any]]:
        """언어능력 목록 반환"""
        pass

    @abstractmethod
    def get_military_info(self) -> Optional[Dict[str, Any]]:
        """병역 정보 반환"""
        pass

    @abstractmethod
    def is_corporate(self) -> bool:
        """법인 직원 여부"""
        pass

    @abstractmethod
    def get_available_sections(self) -> List[str]:
        """사용 가능한 섹션 목록"""
        pass

    @abstractmethod
    def get_profile_id(self) -> int:
        """프로필 ID 반환"""
        pass

    @abstractmethod
    def get_display_name(self) -> str:
        """표시용 이름 반환"""
        pass


class EmployeeProfileAdapter(ProfileAdapter):
    """법인 직원용 어댑터"""

    AVAILABLE_SECTIONS = [
        'basic', 'organization', 'contract', 'salary',
        'benefit', 'insurance', 'education', 'career',
        'certificate', 'language', 'military',
        'employment_contract', 'personnel_movement', 'attendance_assets'
    ]

    def __init__(self, employee):
        self.employee = employee

    def get_basic_info(self) -> Dict[str, Any]:
        return {
            'name': self.employee.name,
            'english_name': self.employee.english_name,
            'chinese_name': self.employee.chinese_name,
            'birth_date': self.employee.birth_date,
            'gender': self.employee.gender,
            'mobile_phone': self.employee.mobile_phone,
            'email': self.employee.email,
            'address': self.employee.address,
            'photo': self.employee.photo,
            'employee_number': self.employee.employee_number,
        }

    def get_organization_info(self) -> Optional[Dict[str, Any]]:
        return {
            'organization': self.employee.organization.to_dict() if self.employee.organization else None,
            'department': self.employee.department,
            'position': self.employee.position,
            'team': self.employee.team,
            'job_title': self.employee.job_title,
            'hire_date': self.employee.hire_date,
            'status': self.employee.status,
            'work_location': self.employee.work_location,
        }

    def get_contract_info(self) -> Optional[Dict[str, Any]]:
        if self.employee.contract:
            return self.employee.contract.to_dict()
        return None

    def get_salary_info(self) -> Optional[Dict[str, Any]]:
        if self.employee.salary:
            return self.employee.salary.to_dict()
        return None

    def get_benefit_info(self) -> Optional[Dict[str, Any]]:
        if self.employee.benefit:
            return self.employee.benefit.to_dict()
        return None

    def get_insurance_info(self) -> Optional[Dict[str, Any]]:
        if self.employee.insurance:
            return self.employee.insurance.to_dict()
        return None

    def get_education_list(self) -> List[Dict[str, Any]]:
        return [edu.to_dict() for edu in self.employee.educations.all()]

    def get_career_list(self) -> List[Dict[str, Any]]:
        return [career.to_dict() for career in self.employee.careers.all()]

    def get_certificate_list(self) -> List[Dict[str, Any]]:
        return [cert.to_dict() for cert in self.employee.certificates.all()]

    def get_language_list(self) -> List[Dict[str, Any]]:
        return [lang.to_dict() for lang in self.employee.languages.all()]

    def get_military_info(self) -> Optional[Dict[str, Any]]:
        if self.employee.military_service:
            return self.employee.military_service.to_dict()
        return None

    def is_corporate(self) -> bool:
        return True

    def get_available_sections(self) -> List[str]:
        return self.AVAILABLE_SECTIONS

    def get_profile_id(self) -> int:
        return self.employee.id

    def get_display_name(self) -> str:
        return f"{self.employee.name} {self.employee.position or ''}"


class PersonalProfileAdapter(ProfileAdapter):
    """일반 개인용 어댑터"""

    AVAILABLE_SECTIONS = [
        'basic', 'education', 'career',
        'certificate', 'language', 'military'
    ]

    def __init__(self, profile):
        self.profile = profile

    def get_basic_info(self) -> Dict[str, Any]:
        return {
            'name': self.profile.name,
            'english_name': self.profile.english_name,
            'birth_date': self.profile.birth_date,
            'gender': self.profile.gender,
            'mobile_phone': self.profile.mobile_phone,
            'email': self.profile.email,
            'address': self.profile.address,
            'photo': self.profile.photo,
        }

    def get_organization_info(self) -> Optional[Dict[str, Any]]:
        return None  # 개인 계정은 소속 정보 없음

    def get_contract_info(self) -> Optional[Dict[str, Any]]:
        return None

    def get_salary_info(self) -> Optional[Dict[str, Any]]:
        return None

    def get_benefit_info(self) -> Optional[Dict[str, Any]]:
        return None

    def get_insurance_info(self) -> Optional[Dict[str, Any]]:
        return None

    def get_education_list(self) -> List[Dict[str, Any]]:
        # PersonalEducation 모델 사용
        return [edu.to_dict() for edu in self.profile.educations.all()]

    def get_career_list(self) -> List[Dict[str, Any]]:
        # PersonalCareer 모델 사용
        return [career.to_dict() for career in self.profile.careers.all()]

    def get_certificate_list(self) -> List[Dict[str, Any]]:
        return [cert.to_dict() for cert in self.profile.certificates.all()]

    def get_language_list(self) -> List[Dict[str, Any]]:
        return [lang.to_dict() for lang in self.profile.languages.all()]

    def get_military_info(self) -> Optional[Dict[str, Any]]:
        if self.profile.military_service:
            return self.profile.military_service.to_dict()
        return None

    def is_corporate(self) -> bool:
        return False

    def get_available_sections(self) -> List[str]:
        return self.AVAILABLE_SECTIONS

    def get_profile_id(self) -> int:
        return self.profile.id

    def get_display_name(self) -> str:
        return self.profile.name
```

### 2.2 통합 데코레이터

**파일**: `app/blueprints/profile/decorators.py`

```python
"""
Profile Decorators - 통합 프로필 인증 데코레이터
"""
from functools import wraps
from flask import session, g, flash, redirect, url_for

from app.models.employee import Employee
from app.models.personal.profile import PersonalProfile
from app.adapters.profile_adapter import (
    EmployeeProfileAdapter,
    PersonalProfileAdapter
)


def unified_profile_required(f):
    """
    통합 프로필 인증 데코레이터

    - 법인 직원: session['employee_id'] 사용
    - 일반 개인: session['user_id'] 사용
    - g.profile에 적절한 어댑터 설정
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        employee_id = session.get('employee_id')

        # 인증 확인
        if not user_id and not employee_id:
            flash('로그인이 필요합니다.', 'warning')
            return redirect(url_for('auth.login'))

        # 어댑터 생성
        if employee_id:
            employee = Employee.query.get(employee_id)
            if not employee:
                flash('직원 정보를 찾을 수 없습니다.', 'error')
                return redirect(url_for('auth.login'))
            g.profile = EmployeeProfileAdapter(employee)
            g.is_corporate = True
        else:
            profile = PersonalProfile.query.filter_by(user_id=user_id).first()
            if not profile:
                # 프로필이 없으면 생성 페이지로
                return redirect(url_for('personal.create_profile'))
            g.profile = PersonalProfileAdapter(profile)
            g.is_corporate = False

        return f(*args, **kwargs)
    return decorated_function


def corporate_only(f):
    """법인 직원 전용 데코레이터"""
    @wraps(f)
    @unified_profile_required
    def decorated_function(*args, **kwargs):
        if not g.is_corporate:
            flash('법인 직원만 접근 가능합니다.', 'warning')
            return redirect(url_for('profile.view'))
        return f(*args, **kwargs)
    return decorated_function
```

### 2.3 Context Processor

**파일**: `app/context_processors/profile_context.py`

```python
"""
Profile Context Processor - 템플릿 전역 변수 주입
"""
from flask import g, session


def inject_profile_context():
    """
    프로필 관련 컨텍스트를 템플릿에 주입

    Returns:
        dict: 템플릿에서 사용할 변수들
    """
    context = {
        'is_corporate': getattr(g, 'is_corporate', False),
        'profile': getattr(g, 'profile', None),
    }

    # 프로필이 있으면 추가 정보 주입
    if context['profile']:
        adapter = context['profile']
        context.update({
            'available_sections': adapter.get_available_sections(),
            'profile_name': adapter.get_display_name(),
            'basic_info': adapter.get_basic_info(),
        })

    return context


def register_context_processors(app):
    """앱에 컨텍스트 프로세서 등록"""
    app.context_processor(inject_profile_context)
```

### 2.4 통합 라우트

**파일**: `app/blueprints/profile/routes.py`

```python
"""
Profile Routes - 통합 프로필 라우트
"""
from flask import Blueprint, render_template, g, request, jsonify
from app.blueprints.profile.decorators import (
    unified_profile_required,
    corporate_only
)

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')


@profile_bp.route('/')
@unified_profile_required
def view():
    """통합 프로필 조회"""
    adapter = g.profile

    context = {
        'basic_info': adapter.get_basic_info(),
        'organization_info': adapter.get_organization_info(),
        'contract_info': adapter.get_contract_info(),
        'salary_info': adapter.get_salary_info(),
        'benefit_info': adapter.get_benefit_info(),
        'insurance_info': adapter.get_insurance_info(),
        'education_list': adapter.get_education_list(),
        'career_list': adapter.get_career_list(),
        'certificate_list': adapter.get_certificate_list(),
        'language_list': adapter.get_language_list(),
        'military_info': adapter.get_military_info(),
        'sections': adapter.get_available_sections(),
    }

    return render_template('profile/unified_profile.html', **context)


@profile_bp.route('/edit')
@unified_profile_required
def edit():
    """통합 프로필 수정"""
    adapter = g.profile

    context = {
        'basic_info': adapter.get_basic_info(),
        'sections': adapter.get_available_sections(),
    }

    return render_template('profile/unified_profile_edit.html', **context)


@profile_bp.route('/section/<section_name>')
@unified_profile_required
def get_section(section_name):
    """섹션별 데이터 API"""
    adapter = g.profile

    if section_name not in adapter.get_available_sections():
        return jsonify({'error': '접근 불가능한 섹션'}), 403

    section_methods = {
        'basic': adapter.get_basic_info,
        'organization': adapter.get_organization_info,
        'contract': adapter.get_contract_info,
        'salary': adapter.get_salary_info,
        'benefit': adapter.get_benefit_info,
        'insurance': adapter.get_insurance_info,
        'education': adapter.get_education_list,
        'career': adapter.get_career_list,
        'certificate': adapter.get_certificate_list,
        'language': adapter.get_language_list,
        'military': adapter.get_military_info,
    }

    method = section_methods.get(section_name)
    if method:
        return jsonify(method())

    return jsonify({'error': '알 수 없는 섹션'}), 404
```

---

## 3. 템플릿 설계

### 3.1 통합 프로필 메인 템플릿

**파일**: `app/templates/profile/unified_profile.html`

```jinja2
{% extends 'base.html' %}

{% block title %}
    {{ '인사카드' if is_corporate else '프로필' }} - {{ profile_name }}
{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/pages/profile.css') }}">
{% endblock %}

{% block content %}
<div class="profile-container" data-account-type="{{ 'corporate' if is_corporate else 'personal' }}">
    {# 헤더 영역 #}
    {% include 'profile/partials/_header_unified.html' %}

    <div class="profile-content">
        {# 사이드 네비게이션 #}
        {% include 'profile/partials/_section_nav_unified.html' %}

        {# 메인 콘텐츠 영역 #}
        <main class="profile-main">
            {# 공통 섹션: 기본 정보 #}
            {% include 'profile/partials/sections/_basic_info.html' %}

            {# 법인 전용 섹션 #}
            {% if is_corporate %}
                {% include 'profile/partials/sections/_organization_info.html' %}
                {% include 'profile/partials/sections/_contract_info.html' %}
                {% include 'profile/partials/sections/_salary_info.html' %}
                {% include 'profile/partials/sections/_benefit_info.html' %}
                {% include 'profile/partials/sections/_insurance_info.html' %}
            {% endif %}

            {# 공통 섹션: 이력 및 경력 #}
            {% include 'profile/partials/sections/_education_info.html' %}
            {% include 'profile/partials/sections/_career_info.html' %}
            {% include 'profile/partials/sections/_certificate_info.html' %}
            {% include 'profile/partials/sections/_language_info.html' %}
            {% include 'profile/partials/sections/_military_info.html' %}

            {# 법인 전용 섹션: 인사기록 #}
            {% if is_corporate %}
                {% include 'profile/partials/sections/_employment_contract.html' %}
                {% include 'profile/partials/sections/_personnel_movement.html' %}
                {% include 'profile/partials/sections/_attendance_assets.html' %}
            {% endif %}
        </main>
    </div>
</div>
{% endblock %}
```

### 3.2 통합 섹션 네비게이션

**파일**: `app/templates/profile/partials/_section_nav_unified.html`

```jinja2
{#
    통합 섹션 네비게이션
    is_corporate: 법인 여부
    available_sections: 사용 가능한 섹션 목록
#}
<aside class="section-nav" id="sectionNav">
    <div class="section-nav-header">
        <div class="section-nav-title">{{ '인사카드' if is_corporate else '프로필' }}</div>
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
            {% if is_corporate %}
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
        </div>

        {# 이력 및 경력 그룹 #}
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

        {# 인사기록 그룹 (법인 전용) #}
        {% if is_corporate %}
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

### 3.3 통합 헤더

**파일**: `app/templates/profile/partials/_header_unified.html`

```jinja2
{#
    통합 프로필 헤더
    is_corporate: 법인 여부
    basic_info: 기본 정보
    organization_info: 소속 정보 (법인만)
#}
<header class="profile-header">
    <div class="profile-header-content">
        {# 프로필 사진 #}
        <div class="profile-photo">
            {% if basic_info.photo %}
            <img src="{{ url_for('static', filename='images/face/' ~ basic_info.photo) }}"
                 alt="{{ basic_info.name }}" class="profile-photo-img">
            {% else %}
            <div class="profile-photo-placeholder">
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

            {% if is_corporate and organization_info %}
            <div class="profile-position">
                {{ organization_info.department or '' }}
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
            {% else %}
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

        {# 명함 영역 (법인 전용) #}
        {% if is_corporate %}
        <div class="profile-business-card">
            {# 명함 업로드/표시 영역 #}
        </div>
        {% endif %}
    </div>
</header>
```

---

## 4. CSS 테마 시스템

**파일**: `app/static/css/pages/profile.css`

```css
/* 통합 프로필 CSS 변수 */
:root {
    /* 기본 테마 (법인) */
    --profile-primary: var(--color-primary-600);
    --profile-accent: var(--color-primary-500);
    --profile-bg: var(--color-gray-50);
    --profile-card-bg: white;
    --profile-border: var(--color-gray-200);
    --profile-text: var(--color-gray-900);
    --profile-text-secondary: var(--color-gray-600);
}

/* 개인 계정 테마 */
[data-account-type="personal"] {
    --profile-primary: #10b981;
    --profile-accent: #059669;
}

/* 프로필 컨테이너 */
.profile-container {
    min-height: 100vh;
    background: var(--profile-bg);
}

/* 프로필 헤더 */
.profile-header {
    background: white;
    border-bottom: 1px solid var(--profile-border);
    padding: 1.5rem 2rem;
}

.profile-header-content {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    max-width: 1400px;
    margin: 0 auto;
}

/* 프로필 사진 */
.profile-photo {
    width: 100px;
    height: 100px;
    border-radius: 50%;
    overflow: hidden;
    border: 3px solid var(--profile-primary);
    flex-shrink: 0;
}

.profile-photo-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.profile-photo-placeholder {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--profile-bg);
    color: var(--profile-text-secondary);
    font-size: 2.5rem;
}

/* 프로필 정보 */
.profile-info {
    flex: 1;
}

.profile-name {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--profile-text);
    margin: 0 0 0.25rem;
}

.profile-name-en {
    font-weight: 400;
    color: var(--profile-text-secondary);
    font-size: 1rem;
}

.profile-position {
    color: var(--profile-primary);
    font-weight: 500;
    margin-bottom: 0.5rem;
}

.profile-meta,
.profile-contact {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
}

.profile-meta-item,
.profile-contact-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: var(--profile-text-secondary);
    font-size: 0.875rem;
}

.profile-meta-item i,
.profile-contact-item i {
    color: var(--profile-primary);
}

/* 콘텐츠 레이아웃 */
.profile-content {
    display: flex;
    max-width: 1400px;
    margin: 0 auto;
    padding: 1.5rem;
    gap: 1.5rem;
}

/* 섹션 네비게이션 */
.section-nav {
    width: 260px;
    flex-shrink: 0;
    position: sticky;
    top: 1.5rem;
    height: fit-content;
}

.section-nav-header {
    background: var(--profile-primary);
    color: white;
    padding: 1rem;
    border-radius: 0.5rem 0.5rem 0 0;
}

.section-nav-title {
    font-weight: 600;
    font-size: 1rem;
}

.section-nav-subtitle {
    font-size: 0.875rem;
    opacity: 0.9;
}

.section-nav-menu {
    background: white;
    border: 1px solid var(--profile-border);
    border-top: none;
    border-radius: 0 0 0.5rem 0.5rem;
}

.section-nav-group {
    padding: 0.75rem 0;
    border-bottom: 1px solid var(--profile-border);
}

.section-nav-group:last-child {
    border-bottom: none;
}

.section-nav-group-title {
    padding: 0.5rem 1rem;
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--profile-text-secondary);
    text-transform: uppercase;
}

.section-nav-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.625rem 1rem;
    color: var(--profile-text);
    text-decoration: none;
    font-size: 0.875rem;
    transition: all 0.2s;
}

.section-nav-item:hover {
    background: var(--profile-bg);
    color: var(--profile-primary);
}

.section-nav-item.active {
    background: rgba(var(--color-primary-rgb), 0.1);
    color: var(--profile-primary);
    font-weight: 500;
}

.section-nav-item i {
    width: 1.25rem;
    text-align: center;
}

/* 메인 콘텐츠 */
.profile-main {
    flex: 1;
    min-width: 0;
}

/* 반응형 */
@media (max-width: 1024px) {
    .profile-content {
        flex-direction: column;
    }

    .section-nav {
        width: 100%;
        position: static;
    }

    .section-nav-menu {
        display: flex;
        flex-wrap: wrap;
    }

    .section-nav-group {
        border-bottom: none;
        border-right: 1px solid var(--profile-border);
    }
}

@media (max-width: 640px) {
    .profile-header-content {
        flex-direction: column;
        text-align: center;
    }

    .profile-meta,
    .profile-contact {
        justify-content: center;
    }
}
```

---

## 5. 마이그레이션 계획

### 5.1 Phase 0: 인프라 준비 (CRITICAL)

**기간**: 1주차

| 작업 | 파일 | 설명 |
|------|------|------|
| ProfileAdapter 구현 | `app/adapters/profile_adapter.py` | 추상 어댑터 + 구현체 |
| 통합 데코레이터 | `app/blueprints/profile/decorators.py` | @unified_profile_required |
| Context Processor | `app/context_processors/profile_context.py` | 템플릿 변수 주입 |
| 기능 플래그 | `config.py` | ENABLE_UNIFIED_PROFILE |

### 5.2 Phase 1: 템플릿 통합 (HIGH)

**기간**: 2-3주차

| 작업 | 파일 | 설명 |
|------|------|------|
| 통합 메인 템플릿 | `templates/profile/unified_profile.html` | 메인 레이아웃 |
| 헤더 partial | `templates/profile/partials/_header_unified.html` | 통합 헤더 |
| 네비게이션 partial | `templates/profile/partials/_section_nav_unified.html` | 사이드 메뉴 |
| 섹션 partials | `templates/profile/partials/sections/` | 14개 섹션 분리 |

### 5.3 Phase 2: 라우트 통합 (HIGH)

**기간**: 4주차

| 작업 | 파일 | 설명 |
|------|------|------|
| 통합 Blueprint | `app/blueprints/profile/__init__.py` | Blueprint 등록 |
| 통합 라우트 | `app/blueprints/profile/routes.py` | /profile/* 라우트 |
| 리다이렉트 | 기존 라우트 | 301 리다이렉트 설정 |

### 5.4 Phase 3: CSS/테마 통합 (MEDIUM)

**기간**: 5주차

| 작업 | 파일 | 설명 |
|------|------|------|
| CSS 변수 | `static/css/pages/profile.css` | 테마 변수 시스템 |
| 반응형 스타일 | 동일 | 모바일 대응 |
| 접근성 개선 | 동일 | WCAG 2.1 AA |

### 5.5 Phase 4: 점진적 롤아웃 (LOW)

**기간**: 6주차

| 단계 | 비율 | 기간 | 롤백 조건 |
|------|------|------|----------|
| Stage 1 | 0% | 준비 | - |
| Stage 2 | 10% | 3일 | 에러율 >1% |
| Stage 3 | 50% | 3일 | 에러율 >0.5% |
| Stage 4 | 100% | 7일 | 에러율 >0.1% |

---

## 6. 검증 체크리스트

### 6.1 기능 검증

- [ ] 법인 직원 프로필 조회 정상 동작
- [ ] 일반 개인 프로필 조회 정상 동작
- [ ] 섹션 네비게이션 정상 동작
- [ ] 조건부 렌더링 정확성
- [ ] 데이터 로딩 성능

### 6.2 UI/UX 검증

- [ ] 법인/개인 테마 색상 적용
- [ ] 반응형 레이아웃 (640px, 768px, 1024px)
- [ ] 접근성 (aria-label, 키보드 네비게이션)
- [ ] 로딩 상태 표시

### 6.3 보안 검증

- [ ] 인증 데코레이터 동작
- [ ] 세션 관리 정상
- [ ] 권한 분리 (법인 전용 섹션)
- [ ] CSRF 토큰 검증

### 6.4 성능 검증

- [ ] 템플릿 렌더링 시간 <500ms
- [ ] 데이터베이스 쿼리 최적화 (N+1 방지)
- [ ] 정적 자원 캐싱

---

## 7. 위험 관리

### 7.1 롤백 계획

| 상황 | 대응 | 소요 시간 |
|------|------|----------|
| 즉시 롤백 | 기능 플래그 비활성화 | 0-5분 |
| DB 롤백 | alembic downgrade -1 | 5-15분 |
| 전체 롤백 | git checkout + 배포 | 15-30분 |

### 7.2 모니터링 지표

| 지표 | 임계값 | 알림 조건 |
|------|--------|----------|
| 응답 시간 P95 | <1.5s | >2s |
| 5xx 에러율 | <0.1% | >0.5% |
| 페이지 뷰 | 기준 대비 | -20% |

---

## 8. 참고 문서

- `claudedocs/account_interface_analysis.md` - 인터페이스 비교 분석
- `claudedocs/interface_integration_review.md` - 다중 전문가 검토 보고서
- `app/models/employee.py` - Employee 모델 정의
- `app/templates/partials/employee_detail/_section_nav.html` - 기존 네비게이션 구조
