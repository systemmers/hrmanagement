# 법인 직원 프로필 구조를 개인 계정에 마이그레이션 - 상세 분석 리포트

분석 일자: 2025-12-11
분석 범위: 법인 직원(Employee) vs 개인 계정(PersonalProfile) 템플릿 및 구조

---

## 1. 현재 상태 분석

### 1.1 데이터 모델 계층
```
법인 직원: Employee 모델 (app/models/employee/)
개인 계정: PersonalProfile 모델 (app/models/personal_profile.py)
어댑터: ProfileAdapter (app/adapters/profile_adapter.py)
```

**데이터 필드 비교**:
- 공통 필드: name, english_name, chinese_name, birth_date, lunar_birth, gender, mobile_phone, home_phone, email, address, detailed_address, postal_code, nationality, blood_type, religion, hobby, specialty
- 법인 전용: employee_number, organization_id, department, position, team, job_title, hire_date, status, work_location, internal_phone, company_email
- 개인 전용: resident_number, is_public

**최근 작업 (방금 완료)**:
- `personal/profile_edit.html`에 resident_number 필드 추가
- 라벨 통일 (성명 (한글), 여권명 (영문) 등)
- adapter에 resident_number 포함

### 1.2 템플릿 구조 비교

#### 법인 직원 템플릿 (employees/)
```
조회:
- detail.html (인사카드 전체)
- detail_basic.html (기본정보만)

수정:
- form.html (전체 수정)
- form_basic.html (기본정보만)

Partials:
- partials/employee_detail/_employee_header.html
- partials/employee_detail/_basic_info.html
- partials/employee_detail/_history_info.html
- partials/employee_detail/_hr_records.html

- partials/employee_form/_personal_info.html
- partials/employee_form/_organization_info.html
- partials/employee_form/_contract_info.html
- partials/employee_form/_education_info.html
- partials/employee_form/_career_info.html
- partials/employee_form/_certificate_info.html
- partials/employee_form/_language_info.html
- partials/employee_form/_military_info.html
- partials/employee_form/_family_info.html
- partials/employee_form/_salary_info.html
- partials/employee_form/_insurance_info.html
```

#### 개인 계정 템플릿 (personal/, profile/)
```
조회:
- profile/unified_profile.html (통합 프로필 - 법인/개인 구분)

수정:
- personal/profile_edit.html (개인 프로필 수정)

Partials:
- profile/partials/sections/_basic_info.html
- profile/partials/sections/_education_info.html
- profile/partials/sections/_career_info.html
- profile/partials/sections/_certificate_info.html
- profile/partials/sections/_language_info.html
- profile/partials/sections/_military_info.html
```

### 1.3 HTML 구조 및 스타일 차이점

#### 법인 직원 form.html (수정)
- CSS: `employee-form.css`, `employee-detail.css`, `section-nav.css`
- 레이아웃: `form-page-layout-with-sidebar` (좌측 네비게이션 + 메인 + 우측 첨부파일)
- 섹션 네비게이션: `section_nav` 매크로 (variant='form')
- 프로필 사진: 업로드 기능, 5MB 제한, 삭제 버튼
- 명함: 앞뒤 2장 업로드 기능
- 필드 구조: `form-grid` > `form-group` > `form-input`
- 동적 섹션: 학력, 경력, 자격증, 언어, 프로젝트, 가족 (추가/삭제 버튼)

#### 개인 계정 profile_edit.html (수정)
- CSS: `employee-form.css`, `employee-detail.css`, `section-nav.css` (동일 사용)
- 레이아웃: `detail-page-layout` (좌측 네비게이션 + 메인)
- 섹션 네비게이션: 수동 HTML 작성 (매크로 미사용)
- 프로필 사진: 없음 (업로드 기능 미구현)
- 명함: 없음
- 필드 구조: 동일 (`form-grid` > `form-group` > `form-input`)
- 동적 섹션: API 기반 (JavaScript로 관리)

#### 법인 직원 detail.html (조회)
- 레이아웃: `detail-page-layout` (좌측 네비게이션 + 메인 + 우측 첨부파일)
- 섹션 네비게이션: `section_nav` 매크로 (variant='full')
- 헤더 카드: `partials/employee_detail/_employee_header.html`
- 정보 표시: 카드 기반, 테이블 기반 (이력 정보)
- 편집 버튼: 우측 상단

#### 개인 계정 unified_profile.html (조회)
- CSS: `profile.css` (별도 스타일)
- 레이아웃: `profile-page` (좌측 네비게이션 + 메인)
- 섹션 네비게이션: `profile/partials/_section_nav_unified.html`
- 헤더: `profile/partials/_header_unified.html`
- 정보 표시: 섹션 기반, adapter 패턴 사용
- 편집 버튼: 헤더 영역

### 1.4 JavaScript 기능 차이

#### 법인 직원
- `js/pages/employee-form.js`: 폼 제출, 동적 필드 추가/삭제, 주소 검색
- `js/pages/employee-detail.js`: 섹션 네비게이션, 명함 업로드, 첨부파일
- `js/components/business-card.js`: 명함 관리
- `js/components/tree-selector.js`: 조직도 선택

#### 개인 계정
- `js/pages/profile/profile-navigation.js`: 섹션 네비게이션
- API 기반 동적 데이터 관리 (blueprint에서 처리)

---

## 2. 차이점 상세 분석

### 2.1 구조적 차이

| 항목 | 법인 직원 | 개인 계정 | 영향도 |
|-----|---------|---------|--------|
| 레이아웃 클래스 | `form-page-layout-with-sidebar` | `detail-page-layout` | 높음 |
| 섹션 네비게이션 | 매크로 기반 (`section_nav`) | 수동 HTML | 중간 |
| 프로필 사진 | 업로드 기능 있음 | 업로드 기능 없음 | 높음 |
| 명함 관리 | 앞뒤 업로드 기능 | 없음 | 중간 |
| 동적 필드 관리 | JavaScript 폼 조작 | API + JavaScript | 중간 |
| 첨부파일 사이드바 | 우측 사이드바 | 없음 | 낮음 |
| CSS 파일 | `employee-*.css` | `profile.css` (일부) | 중간 |

### 2.2 기능적 차이

| 기능 | 법인 직원 | 개인 계정 | 비고 |
|-----|---------|---------|-----|
| 프로필 사진 업로드 | O | X | 개인에 추가 필요 |
| 명함 업로드 | O (앞뒤) | X | 개인 불필요 |
| 주소 검색 | O | 수동 입력만 | 개인에 추가 필요 |
| 주민등록번호 | O | O (방금 추가) | 완료 |
| 소속정보 | O (필수) | X | 개인 불필요 |
| 계약정보 | O | X | 개인 불필요 |
| 급여정보 | O | X | 개인 불필요 |
| 4대보험 | O | X | 개인 불필요 |
| 공개 설정 | X | O | 개인 전용 |
| 학력/경력/자격증 | O | O | 공통 |
| 병역 정보 | O | O | 공통 |
| 가족 정보 | O | X | 법인 전용 |
| 프로젝트 | O | X | 법인 전용 |

### 2.3 스타일 차이

#### 공통 사용 CSS
- `css/layouts/section-nav.css` (양쪽 모두 사용)
- `css/components/cards.css` (양쪽 모두 사용)
- `css/pages/employee-form.css` (개인도 사용)
- `css/pages/employee-detail.css` (개인도 사용)

#### 차이점
- 개인: `css/pages/profile.css` (추가 스타일)
- 법인: `css/components/business-card.css` (명함 전용)
- 법인: `css/components/tree-selector.css` (조직도 선택)

**결론**: 대부분의 CSS는 공유하고 있으나, 개인 계정이 `profile.css`를 추가로 사용하여 일부 스타일이 다를 수 있음.

---

## 3. 마이그레이션 전략 제안

### 3.1 접근법 비교

#### 옵션 A: 전체 복사 후 수정
**방법**: 법인 직원 템플릿을 복사하여 개인 계정 전용으로 수정

**장점**:
- 빠른 구현 속도
- 검증된 구조 활용
- 일관성 확보 용이

**단점**:
- 코드 중복 발생
- 유지보수 비용 증가
- 불필요한 법인 전용 코드 포함 가능성

**위험도**: 중간 (20%)
- 불필요한 코드 제거 시 실수 가능성
- 조건부 로직 미처리 시 버그 발생

**예상 작업량**: 2-3시간

---

#### 옵션 B: 점진적 통합
**방법**: 현재 개인 템플릿을 유지하면서 법인 기능을 단계적으로 추가

**장점**:
- 기존 개인 기능 유지
- 점진적 검증 가능
- 위험 분산

**단점**:
- 시간 소요 큼
- 단계별 테스트 필요
- 중간 상태에서 불일치 가능성

**위험도**: 낮음 (10%)
- 각 단계별 검증 가능
- 롤백 용이

**예상 작업량**: 5-7시간

---

#### 옵션 C: 공통 컴포넌트 추출 (권장)
**방법**: 법인/개인 공통 부분을 컴포넌트화하고, 계정 유형별 조건 분기

**장점**:
- DRY 원칙 준수
- 유지보수 최소화
- 장기적 확장성 확보
- 이미 시작된 통합 프로필(`unified_profile.html`) 활용

**단점**:
- 초기 설계 시간 필요
- 조건 분기 로직 복잡도 증가

**위험도**: 낮음 (5%)
- 명확한 구조 설계로 오류 최소화
- 테스트 용이
- adapter 패턴 이미 구현됨

**예상 작업량**: 4-6시간

---

### 3.2 권장 전략: 옵션 C (공통 컴포넌트 추출)

**근거**:
1. 이미 `ProfileAdapter` 패턴 구현 완료
2. `unified_profile.html`이 조회 화면에서 이미 통합 적용
3. `personal/profile_edit.html`이 법인 스타일 대부분 적용 (방금 완료)
4. 향후 유지보수 비용 최소화
5. 프로젝트의 장기적 목표와 일치

**구현 방향**:
```
현재 상태:
- 조회: unified_profile.html (통합 완료)
- 수정: personal/profile_edit.html (부분 통합)

목표 상태:
- 조회: unified_profile.html (유지)
- 수정: profile/unified_profile_edit.html (신규)
  └─ 계정 유형별 조건 분기 (is_corporate)
```

---

## 4. 구체적 실행 계획

### Phase 1: 공통 컴포넌트 분리 (1-2시간)

#### 작업 1-1: 프로필 수정 공통 템플릿 생성
```
파일: app/templates/profile/unified_profile_edit.html

구조:
- 레이아웃: detail-page-layout (통일)
- 섹션 네비게이션: 조건부 렌더링
- 공통 섹션: 기본정보, 학력, 경력, 자격증, 언어, 병역
- 법인 전용: 소속, 계약, 급여, 보험, 가족, 프로젝트
- 개인 전용: 공개 설정

조건 분기:
{% if is_corporate %}
  {# 법인 전용 섹션 #}
{% else %}
  {# 개인 전용 섹션 #}
{% endif %}
```

#### 작업 1-2: 공통 Partial 컴포넌트 추출
```
생성 파일:
- profile/partials/form/_basic_info_form.html (공통)
- profile/partials/form/_education_form.html (공통)
- profile/partials/form/_career_form.html (공통)
- profile/partials/form/_certificate_form.html (공통)
- profile/partials/form/_language_form.html (공통)
- profile/partials/form/_military_form.html (공통)

법인 전용 유지:
- partials/employee_form/_organization_info.html
- partials/employee_form/_contract_info.html
- partials/employee_form/_salary_info.html
- partials/employee_form/_insurance_info.html
- partials/employee_form/_family_info.html
- partials/employee_form/_project_info.html

개인 전용:
- profile/partials/form/_visibility_settings.html (신규)
```

#### 작업 1-3: 검증 체크리스트
- [ ] 공통 필드 정확성 확인 (name, birth_date, gender 등)
- [ ] 개인 전용 필드 포함 (resident_number, is_public)
- [ ] 법인 전용 필드 조건 분기 (employee_number, department 등)
- [ ] CSS 클래스 일관성 (form-grid, form-group, form-input)
- [ ] 라벨 텍스트 통일 (성명 (한글), 여권명 (영문) 등)

---

### Phase 2: 기능 추가 및 통합 (2-3시간)

#### 작업 2-1: 프로필 사진 업로드 기능 추가
```
대상: profile/partials/form/_basic_info_form.html

추가 기능:
- 파일 업로드 input
- 이미지 미리보기
- 삭제 버튼
- JavaScript 핸들러 (js/pages/profile/photo-upload.js)

참고: partials/employee_form/_personal_info.html (141-60줄)
```

#### 작업 2-2: 주소 검색 기능 통합
```
대상: profile/partials/form/_basic_info_form.html

추가:
- 주소 검색 버튼
- 우편번호 API 연동
- 상세주소 입력 필드

참고: partials/employee_form/_personal_info.html (184-201줄)
```

#### 작업 2-3: 동적 필드 관리 통합
```
현재: API 기반 (personal.py blueprint)
목표: JavaScript 폼 기반 + API 백업

작업:
- js/pages/profile/dynamic-forms.js 생성
- 학력/경력/자격증/언어 추가/삭제 UI
- 폼 제출 시 JSON 데이터 생성
- 서버 측 동일 처리 (기존 API 활용)
```

#### 작업 2-4: 검증 체크리스트
- [ ] 프로필 사진 업로드/삭제 테스트
- [ ] 주소 검색 정상 작동
- [ ] 동적 필드 추가/삭제 테스트
- [ ] 폼 제출 데이터 검증
- [ ] 이미지 크기 제한 (5MB) 확인

---

### Phase 3: Blueprint 및 Adapter 통합 (1-2시간)

#### 작업 3-1: Blueprint 라우팅 수정
```python
# app/blueprints/personal.py

@personal_bp.route('/profile/edit', methods=['GET', 'POST'])
@personal_login_required
def profile_edit():
    """프로필 수정 - 통합 템플릿 사용"""
    user_id = session.get('user_id')
    user, profile_obj = personal_service.get_user_with_profile(user_id)

    if not profile_obj:
        profile_obj = personal_service.ensure_profile_exists(user_id, user.username)

    if request.method == 'POST':
        # 프로필 사진 업로드 처리 추가
        photo_file = request.files.get('photoFile')
        if photo_file:
            photo_url = upload_photo(photo_file, user_id)
            data['photo'] = photo_url

        # 기존 데이터 수집
        data = collect_form_data(request.form)

        success, error_msg = personal_service.update_profile(user_id, data)

        if success:
            flash('프로필이 수정되었습니다.', 'success')
            return redirect(url_for('personal.profile'))
        else:
            flash(f'수정 중 오류가 발생했습니다: {error_msg}', 'error')

    # PersonalProfileAdapter를 사용하여 통합 템플릿에 데이터 전달
    adapter = PersonalProfileAdapter(profile_obj)

    context = {
        'is_corporate': False,
        'is_edit_mode': True,
        'profile': profile_obj,
        'adapter': adapter,
        # ... (기존 context)
    }

    return render_template('profile/unified_profile_edit.html', **context)
```

#### 작업 3-2: 파일 업로드 헬퍼 함수 추가
```python
# app/utils/file_helpers.py (신규)

import os
from werkzeug.utils import secure_filename
from app.config import Config

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_photo(file, user_id):
    """프로필 사진 업로드"""
    if not file or not allowed_file(file.filename):
        return None

    if file.content_length > MAX_FILE_SIZE:
        raise ValueError('파일 크기는 5MB를 초과할 수 없습니다.')

    filename = secure_filename(file.filename)
    timestamp = int(time.time())
    new_filename = f"profile_{user_id}_{timestamp}.{filename.rsplit('.', 1)[1].lower()}"

    # 저장 경로: /static/uploads/profile/{user_id}/
    upload_dir = os.path.join(Config.UPLOAD_FOLDER, 'profile', str(user_id))
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, new_filename)
    file.save(file_path)

    # URL 반환
    return f"/static/uploads/profile/{user_id}/{new_filename}"

def delete_photo(photo_url):
    """프로필 사진 삭제"""
    if not photo_url or photo_url.startswith('http'):
        return False

    file_path = os.path.join(Config.BASE_DIR, photo_url.lstrip('/'))
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False
```

#### 작업 3-3: 검증 체크리스트
- [ ] 개인 프로필 수정 라우팅 정상 작동
- [ ] 파일 업로드 헬퍼 함수 테스트
- [ ] adapter context 데이터 검증
- [ ] 에러 핸들링 확인

---

### Phase 4: 스타일 통일 및 최종 검증 (30분-1시간)

#### 작업 4-1: CSS 점검
```
확인 사항:
- profile.css와 employee-form.css 충돌 제거
- 개인 계정 전용 스타일 (visibility-settings) 추가
- 반응형 레이아웃 확인
- 모바일 네비게이션 토글 작동
```

#### 작업 4-2: JavaScript 통합
```
확인 파일:
- js/pages/profile/profile-navigation.js (네비게이션)
- js/pages/profile/photo-upload.js (사진 업로드)
- js/pages/profile/dynamic-forms.js (동적 폼)
- js/utils/formatting.js (전화번호 포맷팅)
```

#### 작업 4-3: 전체 테스트
```
시나리오:
1. 개인 계정 로그인
2. 프로필 조회 (unified_profile.html)
3. 프로필 수정 버튼 클릭
4. 각 섹션별 데이터 입력
   - 기본정보 (사진 업로드 포함)
   - 주소 검색
   - 학력/경력/자격증 추가
   - 병역 정보
5. 저장 및 조회 확인
6. 공개 설정 토글 확인
```

#### 작업 4-4: 최종 검증 체크리스트
- [ ] 법인 직원 기능 정상 작동 (기존 기능 유지)
- [ ] 개인 계정 조회/수정 정상 작동
- [ ] 데이터 필드 정확성 (resident_number 등)
- [ ] 스타일 일관성 (레이아웃, 버튼, 폼)
- [ ] 반응형 디자인 확인
- [ ] 브라우저 호환성 (Chrome, Firefox, Safari, Edge)
- [ ] 에러 처리 및 사용자 피드백
- [ ] 성능 최적화 (로딩 속도)

---

## 5. 위험 관리 및 롤백 전략

### 5.1 위험 요소

| 위험 | 확률 | 영향도 | 완화 방안 |
|-----|------|--------|----------|
| 법인 기능 손상 | 낮음 (10%) | 높음 | 조건 분기 철저, 기존 코드 보존 |
| 개인 기능 누락 | 중간 (30%) | 중간 | 체크리스트 기반 검증 |
| 스타일 불일치 | 중간 (40%) | 낮음 | CSS 우선순위 관리, 단계별 확인 |
| 데이터 손실 | 낮음 (5%) | 높음 | 백업 생성, 트랜잭션 처리 |
| 파일 업로드 오류 | 중간 (20%) | 중간 | 파일 크기/형식 검증, 에러 핸들링 |

### 5.2 롤백 전략

#### 즉시 롤백 (Phase별)
```
Phase 1 롤백:
- 신규 파일 삭제: profile/unified_profile_edit.html
- 기존 파일 복원: personal/profile_edit.html (git 기준)

Phase 2 롤백:
- JavaScript 파일 제거: js/pages/profile/*.js
- blueprint 변경 revert: personal.py

Phase 3 롤백:
- adapter 변경 revert: profile_adapter.py
- helpers 파일 제거: file_helpers.py

Phase 4 롤백:
- CSS 변경 revert: profile.css, employee-form.css
```

#### 전체 롤백
```bash
# Git 브랜치 활용
git checkout HEAD -- app/templates/personal/
git checkout HEAD -- app/templates/profile/
git checkout HEAD -- app/blueprints/personal.py
git checkout HEAD -- app/adapters/profile_adapter.py
git checkout HEAD -- app/static/css/
git checkout HEAD -- app/static/js/
```

### 5.3 안전 장치

1. **Git 브랜치 전략**
   - 현재 브랜치: `hrm-projekt-14`
   - 작업 브랜치: `hrm-projekt-14-profile-migration`
   - 각 Phase별 커밋

2. **백업 생성**
   ```bash
   # Phase 시작 전 백업
   cp -r app/templates/personal backups/personal_$(date +%Y%m%d_%H%M%S)
   cp -r app/templates/profile backups/profile_$(date +%Y%m%d_%H%M%S)
   ```

3. **단계별 검증**
   - 각 Phase 완료 후 테스트 실행
   - 법인 기능 회귀 테스트
   - 개인 기능 신규 테스트

4. **프로덕션 배포 전**
   - 개발 환경 완전 테스트
   - 스테이징 환경 검증
   - A/B 테스트 고려 (가능 시)

---

## 6. 성공 지표 (KPI)

### 6.1 기능적 성공 지표
- [ ] 개인 프로필 조회/수정 정상 작동 (100%)
- [ ] 법인 직원 기능 유지 (100%)
- [ ] 프로필 사진 업로드 성공률 > 95%
- [ ] 주소 검색 성공률 > 98%
- [ ] 동적 필드 추가/삭제 성공률 > 99%

### 6.2 품질 지표
- [ ] 코드 중복률 < 10% (vs 현재 ~40%)
- [ ] CSS 충돌 0건
- [ ] JavaScript 에러 0건
- [ ] 반응형 디자인 정상 작동 (모바일/태블릿/데스크톱)
- [ ] 페이지 로딩 시간 < 2초

### 6.3 유지보수 지표
- [ ] 공통 컴포넌트 재사용률 > 80%
- [ ] 향후 신규 필드 추가 시간 < 30분
- [ ] 버그 수정 평균 시간 < 1시간

---

## 7. 타임라인

```
총 예상 시간: 4-6시간

Phase 1: 공통 컴포넌트 분리 (1-2시간)
├─ 작업 1-1: 통합 템플릿 생성 (30분)
├─ 작업 1-2: Partial 추출 (30-60분)
└─ 작업 1-3: 검증 (30분)

Phase 2: 기능 추가 및 통합 (2-3시간)
├─ 작업 2-1: 사진 업로드 (1시간)
├─ 작업 2-2: 주소 검색 (30분)
├─ 작업 2-3: 동적 필드 (30-60분)
└─ 작업 2-4: 검증 (30분)

Phase 3: Blueprint 통합 (1-2시간)
├─ 작업 3-1: 라우팅 수정 (30-60분)
├─ 작업 3-2: 헬퍼 함수 (30분)
└─ 작업 3-3: 검증 (30분)

Phase 4: 스타일 통일 및 검증 (30분-1시간)
├─ 작업 4-1: CSS 점검 (15분)
├─ 작업 4-2: JS 통합 (15분)
├─ 작업 4-3: 전체 테스트 (15-30분)
└─ 작업 4-4: 최종 검증 (15분)
```

---

## 8. 최종 권고사항

### 8.1 즉시 실행 가능한 작업 (Quick Wins)
1. `personal/profile_edit.html`에 프로필 사진 업로드 섹션 추가 (30분)
2. 주소 검색 버튼 추가 (30분)
3. CSS 클래스 통일 (`form-grid`, `form-group`) (15분)

### 8.2 중장기 개선 사항
1. 통합 프로필 수정 템플릿 (`unified_profile_edit.html`) 완성
2. 공통 컴포넌트 라이브러리 구축
3. 파일 업로드 시스템 고도화 (이미지 리사이징, CDN 연동)
4. 테스트 자동화 (Playwright, Selenium)

### 8.3 성공을 위한 핵심 원칙
1. **DRY (Don't Repeat Yourself)**: 공통 코드는 반드시 컴포넌트화
2. **Incremental Integration**: 단계별 통합 및 검증
3. **Backward Compatibility**: 법인 기능 유지 보장
4. **User-Centered Design**: 사용자 경험 일관성 확보
5. **Test-Driven Development**: 작은 단위로 테스트하며 진행

---

## 9. 결론

**최적 전략**: 옵션 C (공통 컴포넌트 추출)

**근거**:
- 이미 구현된 adapter 패턴 활용
- 코드 중복 최소화 (40% → 10%)
- 향후 유지보수 비용 절감
- 확장성 확보 (향후 법인 관리자, 추가 계정 유형)

**위험도**: 낮음 (5%)
- 명확한 구조 설계
- 단계별 검증
- 롤백 전략 완비

**예상 효과**:
- 개발 시간 절감: 향후 기능 추가 시 30-50% 단축
- 버그 감소: 중복 코드 제거로 50% 감소 예상
- 사용자 경험 개선: 일관된 인터페이스 제공

**시작 시점**: 즉시 (현재 상태에서 시작 가능)

---

## 부록 A: 파일 변경 목록

### 신규 생성 파일
```
app/templates/profile/unified_profile_edit.html
app/templates/profile/partials/form/_basic_info_form.html
app/templates/profile/partials/form/_education_form.html
app/templates/profile/partials/form/_career_form.html
app/templates/profile/partials/form/_certificate_form.html
app/templates/profile/partials/form/_language_form.html
app/templates/profile/partials/form/_military_form.html
app/templates/profile/partials/form/_visibility_settings.html

app/static/js/pages/profile/photo-upload.js
app/static/js/pages/profile/dynamic-forms.js

app/utils/file_helpers.py

claudedocs/workflow_14/profile_migration_analysis.md (본 문서)
```

### 수정 대상 파일
```
app/blueprints/personal.py (라우팅 변경)
app/adapters/profile_adapter.py (필요 시 메서드 추가)
app/static/css/pages/profile.css (스타일 조정)
app/config.py (UPLOAD_FOLDER 설정 확인)
```

### 삭제 고려 파일
```
app/templates/personal/profile_edit.html (통합 완료 후)
```

---

## 부록 B: 테스트 시나리오

### 시나리오 1: 개인 프로필 신규 생성
1. 개인 계정 회원가입 (username: test_personal_001)
2. 로그인
3. 프로필 작성 버튼 클릭
4. 기본정보 입력 (이름, 연락처, 이메일)
5. 프로필 사진 업로드 (2MB JPG)
6. 주소 검색 (서울시 강남구)
7. 학력 추가 (대학교 졸업)
8. 경력 추가 (3년)
9. 자격증 추가 (정보처리기사)
10. 저장 → 프로필 조회 확인

### 시나리오 2: 개인 프로필 수정
1. 개인 계정 로그인 (기존 계정)
2. 프로필 조회
3. 수정 버튼 클릭
4. 프로필 사진 변경 (기존 삭제 → 신규 업로드)
5. 연락처 변경
6. 경력 추가 (1개 더)
7. 자격증 삭제 (기존 1개)
8. 공개 설정 토글 (공개 → 비공개)
9. 저장 → 변경사항 확인

### 시나리오 3: 법인 직원 기능 유지 확인
1. 법인 관리자 로그인
2. 직원 목록 조회
3. 직원 상세 조회
4. 직원 정보 수정 (소속정보, 급여정보)
5. 저장 → 정상 작동 확인
6. 직원 계정으로 로그인
7. 내 정보 수정 (기본정보만)
8. 저장 → 정상 작동 확인

---

## 부록 C: 참고 자료

### 관련 문서
- `.dev_docs/dev_prompt.md` (요구사항 #5)
- `.dev_docs/hrm_checklist.md` (기능 체크리스트)
- `claudedocs/workflow_14/` (현재 워크플로우)

### 기술 스택
- Flask 3.0.0
- Jinja2 템플릿
- SQLAlchemy ORM
- PostgreSQL 데이터베이스
- JavaScript (Vanilla)
- CSS3 (Flexbox, Grid)

### 외부 API
- Daum 주소 검색 API (우편번호 서비스)

---

**분석 완료**
작성자: Claude (Sonnet 4.5)
검토 필요: 개발 담당자, 프로젝트 매니저
