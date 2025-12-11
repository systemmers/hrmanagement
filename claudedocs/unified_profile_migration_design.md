# 통합 프로필 시스템 리팩토링 설계서

**작성일**: 2025-12-11
**목적**: 개인 계정 프로필을 통합 프로필 시스템으로 마이그레이션하여 코드 중복 제거 및 유지보수성 향상

---

## 1. 현재 상황 분석

### 1.1 프로필 시스템 현황

#### A. 법인 직원 (employee_id 있음)
- **라우트**: `/profile/` (profile_bp)
- **데코레이터**: `@unified_profile_required`
- **어댑터**: `EmployeeProfileAdapter`
- **템플릿**: `profile/unified_profile.html`
- **사용 가능 섹션**: 13개 (기본 + 법인 전용)
  ```python
  ['basic', 'organization', 'contract', 'salary',
   'benefit', 'insurance', 'education', 'career',
   'certificate', 'language', 'military',
   'employment_contract', 'personnel_movement', 'attendance_assets']
  ```

#### B. 개인 계정 (account_type='personal')
- **라우트**: `/personal/profile` (personal_bp)
- **데코레이터**: `@personal_login_required`
- **어댑터**: `PersonalProfileAdapter` (구현됨, 미사용)
- **템플릿**: `personal/profile.html` (별도 템플릿)
- **사용 가능 섹션**: 6개
  ```python
  ['basic', 'education', 'career', 'certificate', 'language', 'military']
  ```

#### C. 법인 관리자 (corporate + no employee_id)
- **프로필**: 없음 (대시보드로 리다이렉트)

### 1.2 코드 중복 분석

#### 중복 영역
1. **템플릿 중복**
   - `personal/profile.html`: 295줄
   - `profile/unified_profile.html`: 63줄
   - 중복 섹션: 기본정보, 학력, 경력, 자격증, 어학, 병역
   - 예상 중복률: 60-70%

2. **어댑터 중복**
   - `EmployeeProfileAdapter`: 259줄
   - `PersonalProfileAdapter`: 108줄
   - 공통 메서드: 11개 (추상 메서드)
   - 예상 중복률: 40-50%

3. **데코레이터 로직 중복**
   - `personal/profile.html` 라우트: 세션 확인, 프로필 조회
   - `unified_profile_required`: 동일한 로직 구현

4. **API 엔드포인트 중복**
   - `/personal/education`, `/personal/career` 등
   - `/profile/section/<section_name>` (통합 API)

### 1.3 기술 부채

#### 높은 위험도
- **ENABLE_UNIFIED_PROFILE 플래그 의존성**
  - 현재: `config.py`에서 환경변수로 관리 (기본값: False)
  - 위험: 플래그가 꺼져 있어 통합 프로필 시스템이 실제 사용되지 않음
  - 영향: PersonalProfileAdapter가 구현되었지만 실제 사용되지 않음

- **라우트 분산**
  - 개인 프로필: `personal_bp`
  - 통합 프로필: `profile_bp`
  - 문제: 두 시스템이 병렬로 존재하여 유지보수 부담

#### 중간 위험도
- **템플릿 구조 차이**
  - `personal/profile.html`: 전통적 HTML 구조
  - `profile/unified_profile.html`: 파셜 기반 모듈화
  - 문제: 마이그레이션 시 UI/UX 일관성 유지 필요

---

## 2. 마이그레이션 전략

### 2.1 목표

#### 핵심 목표
1. **코드 중복 제거**: 두 프로필 시스템을 하나로 통합
2. **호환성 유지**: 기존 라우트 및 API 호환성 보장
3. **점진적 마이그레이션**: 단계별 전환으로 리스크 최소화
4. **사용자 경험 보존**: UI/UX 변경 없이 백엔드만 통합

#### 성공 기준
- 코드 중복률 70% → 20% 이하 감소
- 기존 기능 100% 동작
- 성능 저하 없음
- 테스트 커버리지 80% 이상

### 2.2 마이그레이션 단계

#### Phase 1: 준비 단계 (1-2일)
**목표**: 통합 프로필 시스템 활성화 및 검증

1. **플래그 활성화**
   ```python
   # config.py
   ENABLE_UNIFIED_PROFILE = True  # 환경변수 기본값 변경
   ```

2. **어댑터 검증**
   - PersonalProfileAdapter 테스트 코드 작성
   - 데이터 변환 정확성 검증
   - 섹션 권한 확인

3. **라우트 호환성 테스트**
   - `/profile/` 접근 시 개인 계정 처리 확인
   - 세션 상태별 분기 로직 테스트

**완료 기준**:
- PersonalProfileAdapter 단위 테스트 통과
- 개인 계정으로 `/profile/` 접근 성공
- 법인 직원 프로필 기존 동작 유지

#### Phase 2: 라우트 통합 (2-3일)
**목표**: 개인 프로필 라우트를 통합 프로필로 리다이렉트

1. **리다이렉트 구현**
   ```python
   # personal.py
   @personal_bp.route('/profile')
   @personal_login_required
   def profile():
       """개인 프로필 조회 (통합 프로필로 리다이렉트)"""
       flash('통합 프로필로 이동합니다.', 'info')
       return redirect(url_for('profile.view'))
   ```

2. **메뉴 링크 업데이트**
   - 개인 대시보드: `personal.profile` → `profile.view`
   - 네비게이션 바: 프로필 링크 통일

3. **API 엔드포인트 마이그레이션**
   - `/personal/education` → `/profile/section/education`
   - 기존 API는 호환성 유지 (프록시 방식)
   ```python
   @personal_bp.route('/education', methods=['GET'])
   def education_list():
       """학력 목록 (통합 API로 프록시)"""
       return redirect(url_for('profile.get_section', section_name='education'))
   ```

**완료 기준**:
- 개인 계정 프로필 접근 시 통합 템플릿 표시
- 기존 API 호출 정상 동작 (리다이렉트)
- 브라우저 테스트 통과

#### Phase 3: 템플릿 병합 (3-4일)
**목표**: personal/profile.html 제거 및 통합 템플릿으로 완전 전환

1. **템플릿 비교 분석**
   - 섹션별 마크업 차이 식별
   - CSS 클래스 매핑 작성
   - JavaScript 동작 검증

2. **누락 기능 추가**
   - `personal/profile.html`의 고유 기능 통합 템플릿에 반영
   - 예: 공개/비공개 설정 (is_public)

3. **파셜 템플릿 생성**
   ```
   profile/partials/sections/
   ├─ _basic_info.html (기존)
   ├─ _education_info.html (기존)
   ├─ _career_info.html (기존)
   └─ _personal_settings.html (신규: 개인 전용 설정)
   ```

4. **조건부 렌더링 추가**
   ```jinja
   {# unified_profile.html #}
   {% if not is_corporate %}
       {% include 'profile/partials/sections/_personal_settings.html' %}
   {% endif %}
   ```

**완료 기준**:
- `personal/profile.html` 삭제
- 개인/법인 모두 동일 템플릿 사용
- 시각적 차이 없음 (스크린샷 비교)

#### Phase 4: API 통합 (2-3일)
**목표**: personal_bp의 CRUD API를 profile_bp로 이관

1. **API 엔드포인트 재구성**
   ```python
   # profile/routes.py에 추가
   @profile_bp.route('/education', methods=['POST'])
   @unified_profile_required
   def add_education():
       """학력 추가 (개인/법인 공통)"""
       adapter = g.profile
       data = request.get_json()

       if g.is_corporate:
           # EmployeeEducation 사용
           pass
       else:
           # PersonalEducation 사용
           pass
   ```

2. **Service 계층 통합**
   - `personal_service.py`의 CRUD 로직을 어댑터로 이동
   - 어댑터에 `add_education()`, `delete_education()` 메서드 추가

3. **기존 API 제거**
   - `/personal/education` 등 삭제
   - 클라이언트 코드 업데이트 (JavaScript)

**완료 기준**:
- 모든 CRUD 작업이 `/profile/` 경로에서 동작
- personal_bp에서 프로필 관련 API 제거
- E2E 테스트 통과

#### Phase 5: 정리 및 최적화 (1-2일)
**목표**: 레거시 코드 제거 및 문서화

1. **불필요한 코드 제거**
   ```
   삭제 대상:
   - personal/profile.html
   - personal/profile_edit.html (통합 에디터로 대체 후)
   - personal_bp의 프로필 관련 라우트
   ```

2. **데코레이터 정리**
   - `@personal_login_required` → `@unified_profile_required`로 대체 검토
   - 또는 `@personal_login_required`를 내부적으로 `@unified_profile_required` 호출로 변경

3. **문서 업데이트**
   - API 문서 갱신
   - 아키텍처 다이어그램 수정
   - 마이그레이션 가이드 작성

**완료 기준**:
- 레거시 코드 삭제 완료
- 코드 중복률 20% 이하
- 문서화 완료

---

## 3. 코드 중복 제거 전략

### 3.1 어댑터 패턴 개선

#### 현재 문제점
- `EmployeeProfileAdapter`와 `PersonalProfileAdapter`가 유사한 메서드 구조
- 각 어댑터가 독립적으로 데이터 변환 로직 구현

#### 개선 방안

**공통 Base 어댑터 도입**
```python
# profile_adapter.py
class BaseProfileAdapter(ProfileAdapter):
    """공통 로직을 처리하는 기본 어댑터"""

    def get_basic_info(self) -> Dict[str, Any]:
        """기본 정보 반환 (공통 필드)"""
        model = self._get_model()
        return {
            'id': model.id,
            'name': model.name,
            'english_name': model.english_name,
            'chinese_name': model.chinese_name,
            'birth_date': model.birth_date,
            'lunar_birth': model.lunar_birth,
            'gender': model.gender,
            'mobile_phone': model.mobile_phone,
            'home_phone': model.home_phone,
            'email': model.email,
            # ... 공통 필드
        }

    @abstractmethod
    def _get_model(self):
        """서브클래스에서 구현: 실제 모델 반환"""
        pass

    @abstractmethod
    def _extend_basic_info(self, info: Dict) -> Dict:
        """서브클래스에서 구현: 추가 필드 확장"""
        pass
```

**어댑터별 확장**
```python
class EmployeeProfileAdapter(BaseProfileAdapter):
    def _get_model(self):
        return self.employee

    def _extend_basic_info(self, info: Dict) -> Dict:
        info['employee_number'] = self.employee.employee_number
        info['disability_info'] = self.employee.disability_info
        return info

class PersonalProfileAdapter(BaseProfileAdapter):
    def _get_model(self):
        return self.profile

    def _extend_basic_info(self, info: Dict) -> Dict:
        info['is_public'] = self.profile.is_public
        info['employee_number'] = None
        return info
```

**예상 효과**:
- 코드 중복 50% → 15% 감소
- 유지보수 포인트 단일화

### 3.2 템플릿 파셜화

#### 현재 문제점
- `personal/profile.html`: 295줄 단일 템플릿
- `profile/unified_profile.html`: 파셜 기반이지만 개인 계정 미지원

#### 개선 방안

**섹션별 파셜 구조**
```
profile/partials/sections/
├─ _basic_info.html (공통: 기본정보)
├─ _contact_info.html (공통: 연락처 - personal/profile.html에서 추출)
├─ _address_info.html (공통: 주소 - personal/profile.html에서 추출)
├─ _education_info.html (공통: 학력)
├─ _career_info.html (공통: 경력)
├─ _certificate_info.html (공통: 자격증)
├─ _language_info.html (공통: 어학)
├─ _military_info.html (공통: 병역)
├─ _organization_info.html (법인 전용)
├─ _contract_info.html (법인 전용)
└─ _personal_settings.html (개인 전용: 공개/비공개)
```

**통합 템플릿 구조**
```jinja
{# profile/unified_profile.html #}
<div class="profile-content">
    {# 공통 섹션 #}
    {% include 'profile/partials/sections/_basic_info.html' %}
    {% include 'profile/partials/sections/_contact_info.html' %}
    {% include 'profile/partials/sections/_address_info.html' %}

    {# 법인 전용 섹션 #}
    {% if is_corporate %}
        {% include 'profile/partials/sections/_organization_info.html' %}
        {% include 'profile/partials/sections/_contract_info.html' %}
        {# ... 기타 법인 섹션 #}
    {% endif %}

    {# 공통 이력 섹션 #}
    {% include 'profile/partials/sections/_education_info.html' %}
    {% include 'profile/partials/sections/_career_info.html' %}

    {# 개인 전용 섹션 #}
    {% if not is_corporate %}
        {% include 'profile/partials/sections/_personal_settings.html' %}
    {% endif %}
</div>
```

**예상 효과**:
- 템플릿 중복 70% → 10% 감소
- 섹션 재사용성 향상

### 3.3 API 통합

#### 현재 문제점
- `/personal/education` (POST, DELETE)
- `/profile/section/education` (GET)
- 동일 리소스에 대한 이중 경로

#### 개선 방안

**RESTful 통합 API**
```python
# profile/routes.py
@profile_bp.route('/section/<section_name>', methods=['GET'])
@unified_profile_required
def get_section(section_name):
    """섹션 데이터 조회"""
    # 기존 구현 유지

@profile_bp.route('/section/<section_name>', methods=['POST'])
@unified_profile_required
def add_section_item(section_name):
    """섹션 아이템 추가 (학력, 경력 등)"""
    adapter = g.profile
    data = request.get_json()

    add_methods = {
        'education': adapter.add_education,
        'career': adapter.add_career,
        'certificate': adapter.add_certificate,
        'language': adapter.add_language,
    }

    if section_name not in add_methods:
        return jsonify({'error': '지원하지 않는 섹션'}), 400

    result = add_methods[section_name](data)
    return jsonify({'success': True, 'data': result})

@profile_bp.route('/section/<section_name>/<int:item_id>', methods=['DELETE'])
@unified_profile_required
def delete_section_item(section_name, item_id):
    """섹션 아이템 삭제"""
    adapter = g.profile

    delete_methods = {
        'education': adapter.delete_education,
        'career': adapter.delete_career,
        'certificate': adapter.delete_certificate,
        'language': adapter.delete_language,
    }

    if section_name not in delete_methods:
        return jsonify({'error': '지원하지 않는 섹션'}), 400

    success = delete_methods[section_name](item_id)
    if not success:
        return jsonify({'error': '삭제 실패'}), 404

    return jsonify({'success': True})
```

**어댑터에 CRUD 메서드 추가**
```python
class ProfileAdapter(ABC):
    # 기존 메서드...

    @abstractmethod
    def add_education(self, data: Dict) -> Dict:
        """학력 추가"""
        pass

    @abstractmethod
    def delete_education(self, education_id: int) -> bool:
        """학력 삭제"""
        pass

    # career, certificate, language 동일 패턴

class PersonalProfileAdapter(ProfileAdapter):
    def add_education(self, data: Dict) -> Dict:
        """PersonalEducation 생성"""
        from app.services.personal_service import personal_service
        return personal_service.add_education(self.profile.id, data)

    def delete_education(self, education_id: int) -> bool:
        from app.services.personal_service import personal_service
        return personal_service.delete_education(education_id, self.profile.id)
```

**예상 효과**:
- API 엔드포인트 18개 → 6개 통합
- URL 일관성 향상

---

## 4. 리팩토링 우선순위

### 4.1 위험도/영향도 매트릭스

```
고영향도 |  Phase 3         |  Phase 2
        |  (템플릿 병합)    |  (라우트 통합)
        |  ---------------  |  ---------------
        |  위험: 중         |  위험: 낮
        |  우선순위: 3      |  우선순위: 2
        |                  |
        |------------------|-------------------
        |  Phase 5         |  Phase 1
        |  (정리/최적화)    |  (준비 단계)
저영향도 |  ---------------  |  ---------------
        |  위험: 낮         |  위험: 낮
        |  우선순위: 5      |  우선순위: 1
        |                  |
         저위험도              고위험도
```

### 4.2 단계별 우선순위

| 순위 | Phase | 위험도 | 영향도 | 소요시간 | 비고 |
|-----|-------|-------|-------|---------|-----|
| 1 | Phase 1: 준비 | 낮 | 낮 | 1-2일 | 플래그 활성화, 테스트 |
| 2 | Phase 2: 라우트 통합 | 낮 | 고 | 2-3일 | 사용자 경험 영향 최소 |
| 3 | Phase 3: 템플릿 병합 | 중 | 고 | 3-4일 | UI/UX 변경 가능성 |
| 4 | Phase 4: API 통합 | 중 | 중 | 2-3일 | 클라이언트 코드 영향 |
| 5 | Phase 5: 정리/최적화 | 낮 | 낮 | 1-2일 | 레거시 제거 |

### 4.3 리스크 관리

#### 높은 위험 (Phase 3: 템플릿 병합)
**리스크**:
- 개인 프로필 사용자 UI/UX 변경으로 인한 불만
- CSS 클래스 충돌로 레이아웃 깨짐
- JavaScript 이벤트 핸들러 누락

**완화 전략**:
- 스테이징 환경에서 충분한 테스트
- 스크린샷 비교 자동화 (visual regression testing)
- 롤백 계획 수립 (기존 템플릿 백업 유지)
- 사용자 피드백 수집 기간 확보

#### 중간 위험 (Phase 4: API 통합)
**리스크**:
- 클라이언트 JavaScript 코드 미수정으로 API 호출 실패
- 데이터 변환 로직 누락으로 저장 실패

**완화 전략**:
- API 버전 관리 (v1 유지, v2 신규)
- 프록시 엔드포인트로 호환성 유지
- E2E 테스트 작성 및 실행

---

## 5. 구현 세부사항

### 5.1 데코레이터 통합 방안

#### 옵션 1: unified_profile_required 확장 (권장)
```python
# decorators.py
def unified_profile_required(f):
    """통합 프로필 인증 데코레이터 (개선)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        employee_id = session.get('employee_id')
        account_type = session.get('account_type')

        # 인증 확인
        if not user_id and not employee_id:
            flash('로그인이 필요합니다.', 'warning')
            return redirect(url_for('auth.login'))

        # 법인 직원
        if employee_id:
            employee = Employee.query.get(employee_id)
            if not employee:
                flash('직원 정보를 찾을 수 없습니다.', 'error')
                session.pop('employee_id', None)
                return redirect(url_for('auth.login'))

            g.profile = EmployeeProfileAdapter(employee)
            g.is_corporate = True
            g.employee = employee

        # 법인 관리자 (프로필 없음)
        elif account_type == 'corporate':
            flash('법인 관리자는 개인 프로필이 없습니다.', 'info')
            return redirect(url_for('main.index'))

        # 개인 계정
        else:
            profile = PersonalProfile.query.filter_by(user_id=user_id).first()
            if not profile:
                flash('프로필을 먼저 생성해주세요.', 'info')
                return redirect(url_for('personal.profile_edit'))

            g.profile = PersonalProfileAdapter(profile)
            g.is_corporate = False
            g.personal_profile = profile

        return f(*args, **kwargs)
    return decorated_function
```

**장점**:
- 기존 코드 변경 최소화
- 명확한 통합 시그널

**단점**:
- personal_login_required와 역할 중복

#### 옵션 2: personal_login_required를 얇은 래퍼로 변경
```python
# utils/decorators.py
def personal_login_required(f):
    """개인 계정 인증 데코레이터 (통합 프로필 래퍼)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 기본 인증만 수행
        if not session.get('user_id'):
            flash('로그인이 필요합니다.', 'warning')
            return redirect(url_for('auth.login'))

        # 법인 계정 차단
        if session.get('account_type') == 'corporate':
            flash('개인 계정만 접근 가능합니다.', 'warning')
            return redirect(url_for('main.index'))

        return f(*args, **kwargs)
    return decorated_function
```

**장점**:
- 기존 코드 호환성 유지
- 역할 분리 명확 (인증 vs 프로필 주입)

**단점**:
- 두 데코레이터 조합 필요 시 복잡도 증가

**권장**: 옵션 1 (통합 데코레이터 사용)

### 5.2 라우트 호환성 유지

#### 리다이렉트 방식
```python
# personal.py
@personal_bp.route('/profile')
@personal_login_required
def profile():
    """개인 프로필 조회 (통합 프로필로 리다이렉트)"""
    # 마이그레이션 공지 (선택)
    flash('통합 프로필 시스템으로 이동합니다.', 'info')

    # 통합 프로필로 리다이렉트
    return redirect(url_for('profile.view'), code=301)  # 영구 리다이렉트
```

#### URL 별칭 방식 (Flask 2.0+)
```python
# app/__init__.py
def create_app():
    # ...

    # URL 별칭 등록
    app.add_url_rule(
        '/personal/profile',
        endpoint='personal.profile_alias',
        view_func=lambda: redirect(url_for('profile.view'), code=301)
    )
```

**권장**: 리다이렉트 방식 (명시적, 추적 용이)

### 5.3 템플릿 파셜 추출

#### Step 1: personal/profile.html에서 섹션 추출

**연락처 정보 섹션**
```jinja
{# profile/partials/sections/_contact_info.html #}
<div class="profile-section" id="contact-info">
    <h2 class="section-title">
        <i class="fas fa-phone"></i>
        연락처 정보
    </h2>
    <div class="profile-card">
        <div class="info-grid">
            <div class="info-item">
                <span class="info-label">휴대전화</span>
                <span class="info-value">{{ basic_info.mobile_phone or '-' }}</span>
            </div>
            <div class="info-item">
                <span class="info-label">자택전화</span>
                <span class="info-value">{{ basic_info.home_phone or '-' }}</span>
            </div>
            <div class="info-item">
                <span class="info-label">이메일</span>
                <span class="info-value">{{ basic_info.email or '-' }}</span>
            </div>
        </div>
    </div>
</div>
```

**주소 정보 섹션**
```jinja
{# profile/partials/sections/_address_info.html #}
<div class="profile-section" id="address-info">
    <h2 class="section-title">
        <i class="fas fa-map-marker-alt"></i>
        주소 정보
    </h2>
    <div class="profile-card">
        <div class="info-grid">
            <div class="info-item">
                <span class="info-label">우편번호</span>
                <span class="info-value">{{ basic_info.postal_code or '-' }}</span>
            </div>
            <div class="info-item full-width">
                <span class="info-label">주소</span>
                <span class="info-value">
                    {{ basic_info.address or '' }} {{ basic_info.detailed_address or '' }}
                </span>
            </div>
        </div>
    </div>
</div>
```

#### Step 2: unified_profile.html에 통합
```jinja
{# profile/unified_profile.html #}
<div class="profile-content">
    {# 기본 정보 #}
    {% include 'profile/partials/sections/_basic_info.html' %}

    {# 개인 계정: 연락처/주소 별도 섹션 #}
    {% if not is_corporate %}
        {% include 'profile/partials/sections/_contact_info.html' %}
        {% include 'profile/partials/sections/_address_info.html' %}
    {% endif %}

    {# 법인: 조직 정보 (연락처/주소 포함) #}
    {% if is_corporate %}
        {% include 'profile/partials/sections/_organization_info.html' %}
    {% endif %}

    {# 공통 이력 섹션 #}
    {% include 'profile/partials/sections/_education_info.html' %}
    {% include 'profile/partials/sections/_career_info.html' %}
    {% include 'profile/partials/sections/_certificate_info.html' %}
    {% include 'profile/partials/sections/_language_info.html' %}
    {% include 'profile/partials/sections/_military_info.html' %}
</div>
```

### 5.4 어댑터 CRUD 메서드 구현

```python
# profile_adapter.py

class ProfileAdapter(ABC):
    # 기존 조회 메서드...

    # CRUD 메서드 추가
    @abstractmethod
    def add_education(self, data: Dict) -> Dict:
        """학력 추가"""
        pass

    @abstractmethod
    def update_education(self, education_id: int, data: Dict) -> Dict:
        """학력 수정"""
        pass

    @abstractmethod
    def delete_education(self, education_id: int) -> bool:
        """학력 삭제"""
        pass

    # career, certificate, language 동일 패턴...


class PersonalProfileAdapter(ProfileAdapter):
    """개인 계정 어댑터 (CRUD 구현)"""

    def add_education(self, data: Dict) -> Dict:
        """PersonalEducation 생성"""
        from app.models.personal.education import PersonalEducation
        from app.extensions import db

        edu = PersonalEducation(
            profile_id=self.profile.id,
            school_name=data.get('school_name'),
            major=data.get('major'),
            degree=data.get('degree'),
            admission_date=data.get('admission_date'),
            graduation_date=data.get('graduation_date'),
            status=data.get('status')
        )
        db.session.add(edu)
        db.session.commit()

        return edu.to_dict()

    def update_education(self, education_id: int, data: Dict) -> Dict:
        """PersonalEducation 수정"""
        from app.models.personal.education import PersonalEducation
        from app.extensions import db

        edu = PersonalEducation.query.filter_by(
            id=education_id,
            profile_id=self.profile.id
        ).first()

        if not edu:
            raise ValueError('학력 정보를 찾을 수 없습니다.')

        for key, value in data.items():
            if hasattr(edu, key):
                setattr(edu, key, value)

        db.session.commit()
        return edu.to_dict()

    def delete_education(self, education_id: int) -> bool:
        """PersonalEducation 삭제"""
        from app.models.personal.education import PersonalEducation
        from app.extensions import db

        edu = PersonalEducation.query.filter_by(
            id=education_id,
            profile_id=self.profile.id
        ).first()

        if not edu:
            return False

        db.session.delete(edu)
        db.session.commit()
        return True


class EmployeeProfileAdapter(ProfileAdapter):
    """법인 직원 어댑터 (CRUD 구현)"""

    def add_education(self, data: Dict) -> Dict:
        """EmployeeEducation 생성"""
        from app.models.employee_education import EmployeeEducation
        from app.extensions import db

        edu = EmployeeEducation(
            employee_id=self.employee.id,
            school_name=data.get('school_name'),
            major=data.get('major'),
            degree=data.get('degree'),
            admission_date=data.get('admission_date'),
            graduation_date=data.get('graduation_date'),
            status=data.get('status')
        )
        db.session.add(edu)
        db.session.commit()

        return edu.to_dict()

    # update_education, delete_education 유사 구현...
```

---

## 6. 테스트 전략

### 6.1 단위 테스트

#### 어댑터 테스트
```python
# tests/unit/test_profile_adapter.py
import pytest
from app.adapters.profile_adapter import PersonalProfileAdapter, EmployeeProfileAdapter

class TestPersonalProfileAdapter:
    def test_get_basic_info(self, personal_profile):
        """기본 정보 조회"""
        adapter = PersonalProfileAdapter(personal_profile)
        info = adapter.get_basic_info()

        assert info['name'] == personal_profile.name
        assert info['email'] == personal_profile.email
        assert info['is_public'] == personal_profile.is_public

    def test_add_education(self, personal_profile):
        """학력 추가"""
        adapter = PersonalProfileAdapter(personal_profile)
        data = {
            'school_name': '서울대학교',
            'major': '컴퓨터공학',
            'degree': '학사'
        }

        result = adapter.add_education(data)

        assert result['school_name'] == '서울대학교'
        assert result['major'] == '컴퓨터공학'

    def test_delete_education(self, personal_profile, personal_education):
        """학력 삭제"""
        adapter = PersonalProfileAdapter(personal_profile)

        success = adapter.delete_education(personal_education.id)

        assert success is True

        # 재조회 시 없어야 함
        assert adapter.get_education_list() == []
```

### 6.2 통합 테스트

#### 라우트 테스트
```python
# tests/integration/test_profile_routes.py
import pytest
from flask import url_for

class TestProfileRoutes:
    def test_personal_profile_redirect(self, client, personal_user):
        """개인 프로필 접근 시 통합 프로필로 리다이렉트"""
        # 로그인
        with client.session_transaction() as sess:
            sess['user_id'] = personal_user.id
            sess['account_type'] = 'personal'

        # 개인 프로필 접근
        response = client.get('/personal/profile')

        # 리다이렉트 확인
        assert response.status_code == 301
        assert response.location == url_for('profile.view', _external=False)

    def test_unified_profile_personal(self, client, personal_user, personal_profile):
        """개인 계정 통합 프로필 조회"""
        with client.session_transaction() as sess:
            sess['user_id'] = personal_user.id
            sess['account_type'] = 'personal'

        response = client.get('/profile/')

        assert response.status_code == 200
        assert b'프로필' in response.data
        assert personal_profile.name.encode() in response.data

    def test_education_api(self, client, personal_profile):
        """학력 API 통합"""
        with client.session_transaction() as sess:
            sess['user_id'] = personal_profile.user_id
            sess['account_type'] = 'personal'

        # 학력 추가
        data = {
            'school_name': '서울대학교',
            'major': '컴퓨터공학',
            'degree': '학사'
        }
        response = client.post(
            '/profile/section/education',
            json=data
        )

        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True
        assert result['data']['school_name'] == '서울대학교'
```

### 6.3 E2E 테스트

#### Playwright 시나리오
```python
# tests/e2e/test_profile_migration.py
from playwright.sync_api import expect

def test_personal_profile_flow(page, personal_user):
    """개인 프로필 전체 플로우"""
    # 로그인
    page.goto('/auth/login')
    page.fill('input[name="username"]', personal_user.username)
    page.fill('input[name="password"]', 'password')
    page.click('button[type="submit"]')

    # 프로필 접근
    page.click('a:has-text("프로필")')

    # 통합 프로필 페이지 확인
    expect(page).to_have_url('/profile/')
    expect(page.locator('h1')).to_contain_text('프로필')

    # 학력 추가
    page.click('button:has-text("학력 추가")')
    page.fill('input[name="school_name"]', '서울대학교')
    page.fill('input[name="major"]', '컴퓨터공학')
    page.click('button:has-text("저장")')

    # 추가 확인
    expect(page.locator('.education-list')).to_contain_text('서울대학교')
```

---

## 7. 롤백 계획

### 7.1 긴급 롤백 시나리오

#### Phase별 롤백 전략

**Phase 1-2 롤백**
```python
# config.py
ENABLE_UNIFIED_PROFILE = False  # 플래그 비활성화

# personal.py
@personal_bp.route('/profile')
@personal_login_required
def profile():
    """롤백: 기존 프로필 복원"""
    # 리다이렉트 제거, 기존 로직 복원
    user_id = session.get('user_id')
    user, profile_obj = personal_service.get_user_with_profile(user_id)
    return render_template('personal/profile.html', user=user, profile=profile_obj)
```

**Phase 3 롤백**
- `personal/profile.html` 백업 복원
- 라우트 리다이렉트 제거
- 메뉴 링크 원복

**Phase 4-5 롤백**
- API 엔드포인트 복원
- 클라이언트 JavaScript 원복
- 데이터베이스 마이그레이션 롤백 (필요 시)

### 7.2 백업 전략

#### 코드 백업
```bash
# 각 Phase 시작 전 백업 브랜치 생성
git checkout -b backup/phase-3-before-template-merge
git push origin backup/phase-3-before-template-merge
```

#### 템플릿 백업
```bash
# personal/profile.html 백업
cp app/templates/personal/profile.html \
   app/templates/personal/profile.html.backup
```

### 7.3 모니터링 지표

#### 마이그레이션 성공 지표
- 개인 프로필 접근 에러율 < 1%
- 통합 프로필 로딩 시간 < 500ms
- API 응답 시간 변화율 < 10%

#### 알람 임계값
- 에러율 > 5%: 경고
- 에러율 > 10%: 즉시 롤백
- 응답 시간 > 2초: 성능 조사

---

## 8. 예상 소요 시간 및 리소스

### 8.1 일정

| Phase | 작업 내용 | 소요 시간 | 누적 시간 |
|-------|----------|----------|----------|
| Phase 1 | 준비 단계 (플래그, 테스트) | 1-2일 | 2일 |
| Phase 2 | 라우트 통합 (리다이렉트) | 2-3일 | 5일 |
| Phase 3 | 템플릿 병합 (파셜화) | 3-4일 | 9일 |
| Phase 4 | API 통합 (CRUD) | 2-3일 | 12일 |
| Phase 5 | 정리/최적화 | 1-2일 | 14일 |
| **합계** | | **9-14일** | **14일** |

### 8.2 리소스 배분

#### 개발자 역할
- **백엔드 개발자** (1명): 어댑터, API, 라우트 구현
- **프론트엔드 개발자** (1명): 템플릿 병합, JavaScript 수정
- **QA 엔지니어** (1명): 테스트 작성 및 실행

#### 병렬 작업 가능 영역
- Phase 1-2: 백엔드 위주 (1명)
- Phase 3: 프론트엔드 + 백엔드 병렬 (2명)
- Phase 4: 백엔드 + QA 병렬 (2명)

---

## 9. 성공 지표

### 9.1 정량적 지표

| 지표 | 현재 | 목표 | 측정 방법 |
|-----|-----|-----|----------|
| 코드 중복률 | 70% | < 20% | SonarQube 분석 |
| 템플릿 라인 수 | 358줄 | < 150줄 | 파일 라인 수 집계 |
| API 엔드포인트 | 18개 | 6개 | 라우트 수 카운트 |
| 테스트 커버리지 | 미측정 | > 80% | pytest-cov |
| 평균 응답 시간 | 기준선 | ±10% | New Relic/Datadog |

### 9.2 정성적 지표

- **사용자 경험**: 마이그레이션 전후 동일
- **코드 가독성**: 리뷰어 평가 (5점 척도) > 4점
- **유지보수성**: 신규 기능 추가 소요 시간 -30%

---

## 10. 참고 자료

### 10.1 관련 파일

#### 코어 파일
- `app/blueprints/profile/decorators.py`: 통합 프로필 데코레이터
- `app/blueprints/profile/routes.py`: 통합 프로필 라우트
- `app/blueprints/personal.py`: 개인 프로필 라우트 (마이그레이션 대상)
- `app/adapters/profile_adapter.py`: 프로필 어댑터

#### 템플릿 파일
- `app/templates/profile/unified_profile.html`: 통합 프로필 템플릿
- `app/templates/personal/profile.html`: 개인 프로필 템플릿 (제거 대상)
- `app/templates/profile/partials/sections/*.html`: 섹션 파셜

#### 설정 파일
- `app/config.py`: ENABLE_UNIFIED_PROFILE 플래그

### 10.2 아키텍처 문서
- `.dev_docs/hrm_checklist.md`: Phase 2 개인-법인 분리 아키텍처
- `claudedocs/unified_profile_migration_design.md`: 본 문서

---

## 11. 결론

### 11.1 요약

이 리팩토링은 **개인 프로필과 법인 프로필의 이중 시스템을 단일 통합 시스템으로 통합**하는 작업입니다.

**핵심 전략**:
1. 점진적 마이그레이션 (5단계)
2. 기존 기능 호환성 유지
3. 어댑터 패턴을 통한 데이터 모델 추상화
4. 템플릿 파셜화를 통한 재사용성 극대화

**예상 효과**:
- 코드 중복 70% → 20% 감소
- 유지보수 포인트 단일화
- 신규 기능 추가 시간 30% 단축
- 테스트 커버리지 80% 이상 확보

### 11.2 다음 단계

1. **승인 및 계획 수립** (1일)
   - 이해관계자 리뷰
   - 일정 확정
   - 리소스 할당

2. **Phase 1 시작** (2일)
   - ENABLE_UNIFIED_PROFILE 플래그 활성화
   - PersonalProfileAdapter 테스트 작성 및 검증
   - 스테이징 환경 배포

3. **단계별 진행** (14일)
   - 각 Phase 완료 후 QA 검증
   - 스테이징 → 프로덕션 배포
   - 모니터링 및 피드백 수집

---

**문서 버전**: 1.0
**최종 수정**: 2025-12-11
**작성자**: Claude Code (Refactoring Expert)
**검토자**: (TBD)
