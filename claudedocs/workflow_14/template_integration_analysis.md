# 템플릿 통합 분석 보고서

## 분석 대상
dev_prompt.md #3 요구사항:
- 법인 계정 템플릿을 공통 템플릿으로 하고 프로필을 포함하여 적용
- 일반 개인도 employee 템플릿으로 동일한 템플릿을 사용
- 이미 구축해 놓은 템플릿을 활용

## 현재 상태 분석

### 1. 템플릿 구조 (총 95개 HTML 파일)

```
app/templates/
├── base.html                    # 공통 레이아웃 (109-115줄에서 사이드바 3분기)
├── dashboard/
│   ├── base_dashboard.html      # 통합 대시보드 템플릿 (account_type 분기)
│   ├── _info_corporate.html     # 법인 정보 partial
│   ├── _info_personal.html      # 개인 정보 partial
│   ├── _stats_corporate.html    # 법인 통계 partial
│   ├── _stats_personal.html     # 개인 통계 partial
│   ├── _quick_links_corporate.html
│   ├── _quick_links_personal.html
│   └── _visibility_status.html
├── profile/
│   ├── unified_profile.html     # 통합 프로필 (is_corporate 분기)
│   ├── partials/
│   │   ├── _header_unified.html
│   │   ├── _section_nav_unified.html
│   │   └── sections/            # 섹션별 partial (11개)
│   ├── admin_profile_create.html
│   └── admin_profile_edit.html
├── personal/
│   ├── dashboard.html           # 독립 대시보드 (178줄) - 통합 대상
│   ├── profile.html             # 독립 프로필 (298줄) - 통합 대상
│   ├── profile_edit.html
│   └── register.html
├── corporate/
│   ├── dashboard.html           # 독립 대시보드 (145줄) - 통합 대상
│   ├── settings.html
│   ├── users.html
│   ├── add_user.html
│   └── register.html
├── employees/
│   ├── detail.html              # 직원 상세 (3열 레이아웃)
│   ├── detail_basic.html
│   ├── detail_history.html
│   ├── list.html
│   ├── form.html
│   ├── form_basic.html
│   └── form_history.html
└── components/navigation/
    ├── _sidebar_corporate.html  # 111줄 - 법인 관리자용
    ├── _sidebar_personal.html   # 36줄 - 개인 계정용
    └── _sidebar_employee.html   # 36줄 - 법인 직원용
```

### 2. ProfileAdapter 패턴 분석

현재 3종의 Adapter가 구현되어 있음 (`app/adapters/profile_adapter.py`):

| Adapter | 대상 모델 | AVAILABLE_SECTIONS | is_corporate() |
|---------|----------|-------------------|----------------|
| EmployeeProfileAdapter | Employee | 14개 | True |
| PersonalProfileAdapter | PersonalProfile | 6개 | False |
| CorporateAdminProfileAdapter | CorporateAdminProfile | 2개 | True |

**공통 섹션**: basic, education, career, certificate, language, military
**법인 전용 섹션**: organization, contract, salary, benefit, insurance, employment_contract, personnel_movement, attendance_assets

### 3. 라우트 분석

| 블루프린트 | 프로필 라우트 | 사용 템플릿 | Adapter 사용 |
|-----------|-------------|-----------|-------------|
| profile | /profile/ | unified_profile.html | O (통합) |
| personal | /personal/profile | personal/profile.html | X (직접 접근) |
| employees | /employees/<id> | employees/detail.html | X (직접 접근) |

### 4. 사이드바 분기 로직 (base.html:109-115)

```jinja2
{% if current_user and current_user.account_type == 'personal' %}
    {% include 'components/navigation/_sidebar_personal.html' %}
{% elif current_user and current_user.role == 'employee' and current_user.employee_id %}
    {% include 'components/navigation/_sidebar_employee.html' %}
{% else %}
    {% include 'components/navigation/_sidebar_corporate.html' %}
{% endif %}
```

## 문제점 식별

### P1: 템플릿 중복
- `personal/dashboard.html` (178줄) vs `corporate/dashboard.html` (145줄)
  - 둘 다 `dashboard/base_dashboard.html` (118줄)로 통합 가능
  - 현재 base_dashboard.html이 존재하나 활용되지 않음

### P2: 프로필 템플릿 불일치
- `personal/profile.html` (298줄): 인라인 정의, Adapter 미사용
- `profile/unified_profile.html` (63줄): partials 활용, Adapter 사용
- 동일 기능의 두 템플릿 존재

### P3: 사이드바 분산
- 3개의 독립 사이드바 파일
- 메뉴 수정 시 3곳 동시 변경 필요
- 일관성 유지 어려움

### P4: 라우트 불일치
- personal.profile → personal/profile.html (레거시)
- profile.view → profile/unified_profile.html (신규)
- 사용자 혼란 가능성

## 요구사항 해석

### "법인 계정 템플릿을 공통 템플릿으로"
- `employees/detail.html` 스타일을 기준으로 함
- 3열 레이아웃 (section-nav + main + sidebar)
- partials include 패턴
- ProfileAdapter를 통한 데이터 접근

### "일반 개인도 employee 템플릿으로 동일하게"
- `personal/profile.html` 제거
- `profile/unified_profile.html` 사용
- PersonalProfileAdapter 활용

### "기존 템플릿 활용"
- 신규 개발 최소화
- 기존 partials, adapter 패턴 최대 활용
- 점진적 마이그레이션

## 통합 전략

### Phase 1: 프로필 통합 (우선순위: 높음)

**목표**: personal/profile.html을 unified_profile.html로 대체

**작업 내용**:
1. `personal.py` 라우트 수정
   - `profile()` 함수가 `profile/unified_profile.html` 렌더링
   - PersonalProfileAdapter 사용
2. 템플릿 컨텍스트 통일
   - `profile` 객체 대신 `adapter.get_*()` 메서드 사용
3. `personal/profile.html` deprecated 처리

**예상 코드 변경**:
```python
# personal.py
@personal_bp.route('/profile')
@login_required
def profile():
    profile = PersonalProfile.query.filter_by(user_id=current_user.id).first()
    adapter = PersonalProfileAdapter(profile)

    return render_template('profile/unified_profile.html',
        is_corporate=False,
        profile_name=adapter.get_display_name(),
        basic_info=adapter.get_basic_info(),
        # ... 기타 context
    )
```

### Phase 2: 대시보드 통합 (우선순위: 중간)

**목표**: 독립 대시보드를 base_dashboard.html로 통합

**작업 내용**:
1. `personal.dashboard` 라우트 수정
   - `dashboard/base_dashboard.html` 렌더링
   - `account_type='personal'` 전달
2. `corporate.dashboard` 라우트 수정
   - `dashboard/base_dashboard.html` 렌더링
   - `account_type='corporate'` 전달
3. 기존 독립 대시보드 deprecated

### Phase 3: 사이드바 통합 (우선순위: 낮음)

**목표**: 3개 사이드바를 1개로 통합

**작업 내용**:
1. `_sidebar_unified.html` 생성
   - account_type, role 기반 동적 메뉴
   - 기존 메뉴 항목 모두 포함
2. `base.html` 사이드바 include 단일화
3. 기존 사이드바 파일 deprecated

### Phase 4: 정리 (우선순위: 낮음)

**작업 내용**:
1. deprecated 템플릿 제거 또는 redirect 처리
2. 라우트 정리 (불필요한 중복 제거)
3. 문서 업데이트
4. 통합 테스트

## 위험 요소 및 완화 방안

| 위험 | 영향도 | 완화 방안 |
|-----|-------|---------|
| 기존 URL 변경 | 높음 | redirect 처리, 점진적 deprecation |
| 데이터 표시 불일치 | 중간 | Adapter 메서드 검증, 단위 테스트 |
| CSS/JS 충돌 | 낮음 | 기존 스타일시트 재사용 |
| 사용자 혼란 | 낮음 | 동일한 UX 유지, 변경 공지 |

## 예상 일정

- Phase 1 (프로필 통합): 2-3일
- Phase 2 (대시보드 통합): 1-2일
- Phase 3 (사이드바 통합): 2-3일
- Phase 4 (정리): 1일

**총 예상: 6-9일**

## 결론

현재 HRM 프로젝트는 이미 통합을 위한 기반이 잘 구축되어 있습니다:
- ProfileAdapter 패턴 구현 완료
- unified_profile.html 템플릿 존재
- base_dashboard.html 템플릿 존재
- partials/sections/ 분리 완료

요구사항 #3을 충족하기 위해서는 주로 **라우트 수정**과 **레거시 템플릿 deprecated 처리**가 필요합니다. 신규 개발보다는 기존 구조 활용에 초점을 맞춘 접근이 적합합니다.
