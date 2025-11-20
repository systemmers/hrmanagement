# InsaCard 템플릿 개선 워크플로우

## 분석 개요

- **분석 대상**: 6개 템플릿 파일 (총 1,109 라인)
- **발견된 이슈**: 18개 (CRITICAL: 7, HIGH: 4, MEDIUM: 3, LOW: 4)
- **예상 작업 기간**: 32-48시간

## Phase 1: 보안 및 접근성 (CRITICAL - 8-12시간)

### 1.1 JavaScript 인젝션 취약점 수정
**위치**: `app/templates/employee/detail.html:212`

#### 현재 코드
```html
<button class="btn-delete" onclick="deleteEmployee({{ employee.id }}, '{{ employee.name }}')">삭제</button>
```

#### 개선 계획
- [ ] 인라인 onclick 핸들러 제거
- [ ] data 속성으로 데이터 전달
- [ ] 별도 JS 파일로 이벤트 리스너 분리

#### 구현
```html
<!-- detail.html -->
<button class="btn-delete"
        data-employee-id="{{ employee.id }}"
        data-employee-name="{{ employee.name }}">삭제</button>

<!-- static/js/employee.js -->
document.querySelectorAll('.btn-delete').forEach(btn => {
    btn.addEventListener('click', function() {
        const id = this.dataset.employeeId;
        const name = this.dataset.employeeName;
        deleteEmployee(id, name);
    });
});
```

#### 검증
- [ ] XSS 공격 시나리오 테스트
- [ ] 특수문자 포함 이름 테스트
- [ ] CSP(Content Security Policy) 정책 준수 확인

---

### 1.2 IndexError 방지
**위치**: `app/templates/base.html:40, 94`

#### 현재 코드
```html
<div class="user-avatar">{{ current_user.name[0] }}</div>
```

#### 개선 계획
- [ ] 안전한 문자 접근 템플릿 필터 생성
- [ ] 빈 문자열 예외 처리
- [ ] 기본값 제공

#### 구현
```python
# app/__init__.py
@app.template_filter('first_char')
def first_char(text):
    """안전하게 첫 글자 반환"""
    return text[0] if text and len(text) > 0 else '?'
```

```html
<!-- base.html -->
<div class="user-avatar">{{ current_user.name | first_char }}</div>
```

#### 검증
- [ ] 빈 이름 테스트
- [ ] None 값 테스트
- [ ] 특수문자 이름 테스트

---

### 1.3 키보드 접근성 개선
**위치**: `app/templates/employee/index.html:50`

#### 현재 코드
```html
<div class="employee-card" onclick="window.location.href='{{ url_for('employee.detail', id=employee.id) }}'">
```

#### 개선 계획
- [ ] div를 semantic HTML로 교체
- [ ] tabindex 및 ARIA 속성 추가
- [ ] 키보드 네비게이션 지원

#### 구현
```html
<a href="{{ url_for('employee.detail', id=employee.id) }}"
   class="employee-card"
   role="button"
   aria-label="{{ employee.name }} 직원 상세 정보 보기">
    <!-- 카드 내용 -->
</a>
```

#### 검증
- [ ] Tab 키 네비게이션 테스트
- [ ] Enter/Space 키 활성화 테스트
- [ ] 스크린 리더 호환성 테스트

---

### 1.4 ARIA 속성 추가

#### 1.4.1 검색 입력 필드
**위치**: `app/templates/employee/index.html`

```html
<div class="search-box" role="search">
    <input type="text"
           id="searchInput"
           placeholder="이름, 부서, 직급으로 검색"
           aria-label="직원 검색"
           aria-describedby="search-help">
    <span id="search-help" class="sr-only">직원의 이름, 부서 또는 직급을 입력하여 검색하세요</span>
</div>
```

#### 1.4.2 필수 입력 필드
**위치**: `app/templates/employee/register.html`, `edit.html`

```html
<input type="text"
       id="name"
       name="name"
       required
       aria-required="true"
       aria-describedby="name-error">
<span id="name-error" class="error-message" role="alert"></span>
```

#### 1.4.3 알림 메시지
**위치**: `app/templates/base.html`

```html
<div class="alert alert-{{ category }}" role="alert" aria-live="polite">
    {{ message }}
</div>
```

#### 체크리스트
- [ ] role="search" 추가 (index.html)
- [ ] aria-required 추가 (register.html, edit.html)
- [ ] aria-describedby 추가 (모든 입력 필드)
- [ ] role="alert" 추가 (flash 메시지)
- [ ] aria-label 추가 (아이콘 버튼)

---

### 1.5 파일 업로드 보안 검증
**위치**: `app/routes/employee.py`

#### 개선 계획
- [ ] MIME 타입 검증
- [ ] 파일 크기 제한
- [ ] 파일 확장자 화이트리스트
- [ ] 안전한 파일명 생성

#### 구현
```python
from werkzeug.utils import secure_filename
import os

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@employee.route('/register', methods=['POST'])
def register():
    if 'photo' in request.files:
        file = request.files['photo']
        if file.filename:
            # 파일 크기 체크
            file.seek(0, os.SEEK_END)
            size = file.tell()
            file.seek(0)

            if size > MAX_FILE_SIZE:
                flash('파일 크기는 5MB를 초과할 수 없습니다.', 'error')
                return redirect(url_for('employee.register'))

            # 확장자 체크
            if not allowed_file(file.filename):
                flash('허용되지 않는 파일 형식입니다.', 'error')
                return redirect(url_for('employee.register'))

            # 안전한 파일명
            filename = secure_filename(file.filename)
            # ... 저장 로직
```

#### 검증
- [ ] 악성 파일 업로드 시도 차단 확인
- [ ] 대용량 파일 업로드 차단 확인
- [ ] 파일명 특수문자 처리 확인

---

## Phase 2: 코드 품질 (HIGH - 16-24시간)

### 2.1 CSS 중복 제거 (450+ 라인)

#### 현재 상태
- register.html: 150+ 라인 CSS
- edit.html: 150+ 라인 CSS
- detail.html: 50+ 라인 CSS
- login.html: 100+ 라인 CSS

#### 개선 계획
- [ ] `static/css/forms.css` 생성
- [ ] 공통 스타일 이동
- [ ] CSS 변수 활용
- [ ] 템플릿에서 `<style>` 태그 제거

#### 구현
```css
/* static/css/forms.css */
:root {
    --form-max-width: 800px;
    --input-height: 48px;
    --input-border: 1px solid #ddd;
    --input-border-focus: 2px solid #007bff;
    --input-border-radius: 8px;
}

.form-container {
    max-width: var(--form-max-width);
    margin: 0 auto;
    padding: 40px;
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.form-group {
    margin-bottom: 24px;
}

.form-label {
    display: block;
    margin-bottom: 8px;
    font-weight: 500;
    color: #333;
}

.form-input {
    width: 100%;
    height: var(--input-height);
    padding: 0 16px;
    border: var(--input-border);
    border-radius: var(--input-border-radius);
    font-size: 15px;
    transition: all 0.2s;
}

.form-input:focus {
    outline: none;
    border: var(--input-border-focus);
}

.form-error {
    color: #dc3545;
    font-size: 14px;
    margin-top: 4px;
}

.btn-primary {
    width: 100%;
    height: 48px;
    background: #007bff;
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 16px;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.2s;
}

.btn-primary:hover {
    background: #0056b3;
}
```

#### 체크리스트
- [ ] forms.css 파일 생성
- [ ] 공통 스타일 이동 (register.html)
- [ ] 공통 스타일 이동 (edit.html)
- [ ] 공통 스타일 이동 (detail.html)
- [ ] 공통 스타일 이동 (login.html)
- [ ] 템플릿에서 `<style>` 블록 제거
- [ ] base.html에 CSS 링크 추가
- [ ] 스타일 적용 검증

---

### 2.2 재사용 가능한 컴포넌트 생성

#### 개선 계획
- [ ] `app/templates/components/` 디렉토리 생성
- [ ] Jinja2 매크로 작성
- [ ] 템플릿에서 매크로 활용

#### 구현

**components/page_header.html**
```jinja2
{% macro render_page_header(title, subtitle=None, actions=None) %}
<div class="page-header">
    <div class="header-content">
        <h1 class="page-title">{{ title }}</h1>
        {% if subtitle %}
        <p class="page-subtitle">{{ subtitle }}</p>
        {% endif %}
    </div>
    {% if actions %}
    <div class="header-actions">
        {{ actions }}
    </div>
    {% endif %}
</div>
{% endmacro %}
```

**components/form_field.html**
```jinja2
{% macro render_field(field, label, type='text', required=False, help_text=None) %}
<div class="form-group">
    <label for="{{ field }}" class="form-label">
        {{ label }}
        {% if required %}<span class="required">*</span>{% endif %}
    </label>
    <input type="{{ type }}"
           id="{{ field }}"
           name="{{ field }}"
           class="form-input"
           {% if required %}required aria-required="true"{% endif %}
           {% if help_text %}aria-describedby="{{ field }}-help"{% endif %}>
    {% if help_text %}
    <span id="{{ field }}-help" class="form-help">{{ help_text }}</span>
    {% endif %}
    <span id="{{ field }}-error" class="form-error" role="alert"></span>
</div>
{% endmacro %}
```

**components/status_badge.html**
```jinja2
{% macro render_status(status) %}
{% set status_config = {
    'active': {'text': '재직', 'class': 'status-active'},
    'warning': {'text': '갱신필요', 'class': 'status-warning'},
    'expired': {'text': '만료', 'class': 'status-expired'}
} %}
{% set config = status_config.get(status, {'text': status, 'class': 'status-default'}) %}
<span class="status-badge {{ config.class }}">{{ config.text }}</span>
{% endmacro %}
```

**components/photo_upload.html**
```jinja2
{% macro render_photo_upload(field_name='photo', current_photo=None, required=False) %}
<div class="photo-upload-container">
    <label class="form-label">
        프로필 사진
        {% if required %}<span class="required">*</span>{% endif %}
    </label>
    <div class="photo-preview-area">
        {% if current_photo %}
        <img id="photoPreview" src="{{ url_for('static', filename=current_photo) }}" alt="프로필 미리보기">
        {% else %}
        <div id="photoPreview" class="photo-placeholder">
            <svg><!-- 카메라 아이콘 --></svg>
            <p>사진을 선택하세요</p>
        </div>
        {% endif %}
    </div>
    <input type="file"
           id="{{ field_name }}"
           name="{{ field_name }}"
           accept="image/*"
           {% if required %}required{% endif %}
           aria-label="프로필 사진 업로드">
    <span class="form-help">JPG, PNG 형식, 최대 5MB</span>
</div>
{% endmacro %}
```

#### 사용 예시
```jinja2
{% from 'components/page_header.html' import render_page_header %}
{% from 'components/form_field.html' import render_field %}
{% from 'components/status_badge.html' import render_status %}
{% from 'components/photo_upload.html' import render_photo_upload %}

{{ render_page_header('직원 등록', subtitle='새로운 직원 정보를 등록합니다') }}

{{ render_field('name', '이름', required=True) }}
{{ render_field('email', '이메일', type='email', help_text='회사 이메일 주소를 입력하세요') }}
{{ render_status(employee.status) }}
{{ render_photo_upload('photo', employee.photo) }}
```

#### 체크리스트
- [ ] components/ 디렉토리 생성
- [ ] page_header.html 매크로 작성
- [ ] form_field.html 매크로 작성
- [ ] status_badge.html 매크로 작성
- [ ] photo_upload.html 매크로 작성
- [ ] register.html에 매크로 적용
- [ ] edit.html에 매크로 적용
- [ ] detail.html에 매크로 적용
- [ ] index.html에 매크로 적용
- [ ] 코드 라인 수 감소 확인 (목표: 30% 이상)

---

### 2.3 관심사 분리 (Separation of Concerns)

#### 현재 문제
**위치**: `app/templates/employee/index.html:75-85`

```html
<span class="status-badge status-{{ employee.status }}">
    {% if employee.status == 'active' %}재직
    {% elif employee.status == 'warning' %}갱신필요
    {% elif employee.status == 'expired' %}만료
    {% endif %}
</span>
```

#### 개선 계획
- [ ] 비즈니스 로직을 Python으로 이동
- [ ] 템플릿 필터 또는 모델 메서드 활용
- [ ] 템플릿은 표현만 담당

#### 구현

**app/models.py**
```python
class Employee(db.Model):
    # ... 기존 필드들

    @property
    def status_display(self):
        """상태 표시 텍스트 반환"""
        status_map = {
            'active': '재직',
            'warning': '갱신필요',
            'expired': '만료'
        }
        return status_map.get(self.status, self.status)

    @property
    def status_class(self):
        """상태 CSS 클래스 반환"""
        return f'status-{self.status}'

    def get_work_duration(self):
        """근무 기간 계산"""
        if not self.hire_date:
            return None
        today = date.today()
        years = today.year - self.hire_date.year
        months = today.month - self.hire_date.month
        if months < 0:
            years -= 1
            months += 12
        return {'years': years, 'months': months}

    def get_work_duration_display(self):
        """근무 기간 표시 텍스트"""
        duration = self.get_work_duration()
        if not duration:
            return '-'
        if duration['years'] > 0:
            return f"{duration['years']}년 {duration['months']}개월"
        return f"{duration['months']}개월"
```

**템플릿 사용**
```html
<span class="status-badge {{ employee.status_class }}">
    {{ employee.status_display }}
</span>

<p class="work-duration">근무 기간: {{ employee.get_work_duration_display() }}</p>
```

#### 체크리스트
- [ ] Employee 모델에 프로퍼티 추가
- [ ] 템플릿 조건문 제거 (index.html)
- [ ] 템플릿 조건문 제거 (detail.html)
- [ ] 근무 기간 계산 로직 이동
- [ ] 단위 테스트 작성

---

## Phase 3: 성능 최적화 (MEDIUM - 8-12시간)

### 3.1 이미지 최적화

#### 개선 계획
- [ ] 이미지 lazy loading 적용
- [ ] width/height 속성 추가 (CLS 방지)
- [ ] srcset 활용 (반응형 이미지)
- [ ] WebP 포맷 지원

#### 구현

**components/employee_photo.html**
```jinja2
{% macro render_employee_photo(photo_path, name, size='medium', lazy=True) %}
{% set sizes = {
    'small': {'width': 80, 'height': 80},
    'medium': {'width': 200, 'height': 200},
    'large': {'width': 400, 'height': 400}
} %}
{% set dim = sizes.get(size, sizes['medium']) %}

<picture>
    <source type="image/webp"
            srcset="{{ url_for('static', filename=photo_path|replace('.png', '.webp')|replace('.jpg', '.webp')) }}">
    <img src="{{ url_for('static', filename=photo_path) }}"
         alt="{{ name }} 프로필 사진"
         width="{{ dim.width }}"
         height="{{ dim.height }}"
         {% if lazy %}loading="lazy"{% endif %}
         class="employee-photo employee-photo-{{ size }}">
</picture>
{% endmacro %}
```

**Python 이미지 처리 (utils/image.py)**
```python
from PIL import Image
import os

def optimize_image(input_path, output_path, quality=85):
    """이미지 최적화 및 WebP 변환"""
    img = Image.open(input_path)

    # WebP 저장
    webp_path = output_path.replace('.png', '.webp').replace('.jpg', '.webp')
    img.save(webp_path, 'WebP', quality=quality)

    # 원본 포맷 최적화
    img.save(output_path, quality=quality, optimize=True)

    return webp_path, output_path
```

#### 체크리스트
- [ ] employee_photo.html 매크로 작성
- [ ] 이미지 최적화 유틸리티 작성
- [ ] 기존 프로필 이미지 WebP 변환
- [ ] lazy loading 적용 (index.html)
- [ ] width/height 속성 추가 (모든 이미지)
- [ ] Lighthouse 성능 점수 측정

---

### 3.2 외부 리소스 보안 (SRI)

#### 현재 코드
**위치**: `app/templates/base.html`

```html
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
```

#### 개선 계획
- [ ] Subresource Integrity (SRI) 해시 추가
- [ ] crossorigin 속성 추가
- [ ] 리소스 힌트 추가 (dns-prefetch, preconnect)

#### 구현
```html
<!-- DNS prefetch -->
<link rel="dns-prefetch" href="https://cdnjs.cloudflare.com">
<link rel="preconnect" href="https://cdnjs.cloudflare.com" crossorigin>

<!-- SRI 적용 -->
<link rel="stylesheet"
      href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"
      integrity="sha512-9usAa10IRO0HhonpyAIVpjrylPvoDwiPUiKdWk5t3PyolY1cOd4DSE0Ga+ri4AuTroPR5aQvXU9xC6qOPnzFeg=="
      crossorigin="anonymous"
      referrerpolicy="no-referrer">
```

#### SRI 해시 생성 스크립트
```bash
#!/bin/bash
# scripts/generate_sri.sh

URL="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"
curl -s "$URL" | openssl dgst -sha512 -binary | openssl base64 -A
```

#### 체크리스트
- [ ] SRI 해시 생성
- [ ] base.html에 integrity 속성 추가
- [ ] crossorigin 속성 추가
- [ ] 리소스 힌트 추가
- [ ] CSP 헤더 설정 검토

---

### 3.3 CSS 변수 일관성

#### 현재 상태
- base.html: `:root` 변수 정의 있음
- 일부 템플릿: 하드코딩된 색상 값 사용

#### 개선 계획
- [ ] 모든 색상을 CSS 변수로 통일
- [ ] 디자인 토큰 시스템 구축
- [ ] 다크모드 준비

#### 구현

**static/css/variables.css**
```css
:root {
    /* Colors - Primary */
    --color-primary: #007bff;
    --color-primary-dark: #0056b3;
    --color-primary-light: #e3f2fd;

    /* Colors - Status */
    --color-success: #28a745;
    --color-warning: #ffc107;
    --color-danger: #dc3545;
    --color-info: #17a2b8;

    /* Colors - UI */
    --color-background: #f8f9fa;
    --color-surface: #ffffff;
    --color-border: #dee2e6;
    --color-text: #212529;
    --color-text-secondary: #6c757d;

    /* Spacing */
    --spacing-xs: 4px;
    --spacing-sm: 8px;
    --spacing-md: 16px;
    --spacing-lg: 24px;
    --spacing-xl: 32px;
    --spacing-2xl: 48px;

    /* Typography */
    --font-size-xs: 12px;
    --font-size-sm: 14px;
    --font-size-base: 16px;
    --font-size-lg: 18px;
    --font-size-xl: 24px;
    --font-size-2xl: 32px;

    /* Border Radius */
    --radius-sm: 4px;
    --radius-md: 8px;
    --radius-lg: 12px;
    --radius-full: 9999px;

    /* Shadows */
    --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
    --shadow-md: 0 2px 8px rgba(0,0,0,0.1);
    --shadow-lg: 0 4px 16px rgba(0,0,0,0.15);

    /* Transitions */
    --transition-fast: 0.15s ease;
    --transition-base: 0.2s ease;
    --transition-slow: 0.3s ease;
}

/* Dark Mode Support (준비) */
@media (prefers-color-scheme: dark) {
    :root {
        --color-background: #1a1a1a;
        --color-surface: #2d2d2d;
        --color-border: #404040;
        --color-text: #f8f9fa;
        --color-text-secondary: #adb5bd;
    }
}
```

#### 하드코딩 제거 예시
```css
/* Before */
.status-active {
    background: #28a745;
    color: white;
}

/* After */
.status-active {
    background: var(--color-success);
    color: var(--color-surface);
}
```

#### 체크리스트
- [ ] variables.css 파일 생성
- [ ] 디자인 토큰 정의
- [ ] 하드코딩 색상 변수로 교체 (base.html)
- [ ] 하드코딩 색상 변수로 교체 (forms.css)
- [ ] 하드코딩 색상 변수로 교체 (각 템플릿)
- [ ] 다크모드 미디어 쿼리 추가

---

## Phase 4: 추가 개선사항 (LOW - 8-12시간)

### 4.1 반응형 이미지

#### 구현
```html
<img src="{{ url_for('static', filename=photo) }}"
     srcset="{{ url_for('static', filename=photo|thumbnail(400)) }} 400w,
             {{ url_for('static', filename=photo|thumbnail(800)) }} 800w,
             {{ url_for('static', filename=photo|thumbnail(1200)) }} 1200w"
     sizes="(max-width: 600px) 400px,
            (max-width: 1200px) 800px,
            1200px"
     alt="{{ name }}">
```

### 4.2 CSP 헤더 설정

**app/__init__.py**
```python
@app.after_request
def set_security_headers(response):
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "style-src 'self' https://cdnjs.cloudflare.com; "
        "font-src 'self' https://cdnjs.cloudflare.com; "
        "img-src 'self' data:; "
        "script-src 'self'"
    )
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response
```

### 4.3 템플릿 캐싱

**config.py**
```python
class ProductionConfig(Config):
    TEMPLATES_AUTO_RELOAD = False
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1년
```

### 4.4 국제화 (i18n) 준비

**app/__init__.py**
```python
from flask_babel import Babel

babel = Babel(app)

@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(['ko', 'en'])
```

---

## 검증 및 테스트

### 자동화 테스트
```bash
# 접근성 테스트
npm install -g pa11y
pa11y http://localhost:5001

# 성능 테스트
npm install -g lighthouse
lighthouse http://localhost:5001 --view

# 보안 테스트
pip install safety
safety check
```

### 수동 검증 체크리스트
- [ ] 키보드만으로 모든 기능 접근 가능
- [ ] 스크린 리더 호환성 (NVDA/JAWS)
- [ ] 다양한 브라우저 테스트 (Chrome, Firefox, Safari, Edge)
- [ ] 모바일 반응형 확인
- [ ] 성능 점수 90+ (Lighthouse)
- [ ] 접근성 점수 90+ (Lighthouse)
- [ ] XSS 공격 시나리오 테스트

---

## 예상 일정

| Phase | 작업 내용 | 예상 시간 | 우선순위 |
|-------|----------|----------|---------|
| Phase 1 | 보안 및 접근성 | 8-12시간 | CRITICAL |
| Phase 2 | 코드 품질 | 16-24시간 | HIGH |
| Phase 3 | 성능 최적화 | 8-12시간 | MEDIUM |
| Phase 4 | 추가 개선사항 | 8-12시간 | LOW |
| **총계** | | **40-60시간** | |

---

## 진행 상황 추적

### Phase 1: 보안 및 접근성
- [ ] 1.1 JavaScript 인젝션 수정
- [ ] 1.2 IndexError 방지
- [ ] 1.3 키보드 접근성
- [ ] 1.4 ARIA 속성
- [ ] 1.5 파일 업로드 보안

### Phase 2: 코드 품질
- [ ] 2.1 CSS 중복 제거
- [ ] 2.2 컴포넌트 생성
- [ ] 2.3 관심사 분리

### Phase 3: 성능 최적화
- [ ] 3.1 이미지 최적화
- [ ] 3.2 SRI 적용
- [ ] 3.3 CSS 변수 통일

### Phase 4: 추가 개선
- [ ] 4.1 반응형 이미지
- [ ] 4.2 CSP 헤더
- [ ] 4.3 템플릿 캐싱
- [ ] 4.4 i18n 준비

---

## 참고 자료

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/3.0.x/security/)
- [Jinja2 Template Designer Documentation](https://jinja.palletsprojects.com/templates/)
- [Web.dev Performance](https://web.dev/performance/)
