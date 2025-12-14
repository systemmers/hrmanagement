# Backend Static File Integration Analysis

## 분석 날짜
2025-12-14

## 1. Static Files Organization

### 1.1 디렉토리 구조
```
app/static/
├── css/                    # 총 ~3,761 라인
│   ├── core/              # 기본 스타일
│   │   ├── variables.css  # CSS 변수 정의
│   │   ├── reset.css
│   │   ├── theme.css
│   │   ├── utilities.css
│   │   └── responsive.css
│   ├── layouts/           # 레이아웃 스타일
│   │   ├── header.css
│   │   ├── sidebar.css
│   │   ├── section-nav.css
│   │   └── main-content.css
│   ├── components/        # 컴포넌트별 스타일 (모듈화)
│   │   ├── button.css
│   │   ├── forms.css
│   │   ├── modal.css
│   │   ├── salary-*.css   # 급여 관련 분리
│   │   ├── data-table-advanced.css
│   │   └── ... (25+ 컴포넌트)
│   └── pages/             # 페이지별 스타일
│       ├── profile.css
│       ├── account.css
│       └── company-card-list.css
├── js/                    # 총 51개 파일
│   ├── app.js             # 메인 진입점 (ES6 모듈)
│   ├── components/        # 재사용 가능 컴포넌트
│   │   ├── toast.js
│   │   ├── form-validator.js
│   │   ├── file-upload.js
│   │   ├── salary/        # 급여 계산기 모듈
│   │   └── data-table/    # 데이터 테이블 모듈 (8개 파일)
│   ├── pages/             # 페이지별 스크립트
│   │   ├── employee/      # 직원 폼 모듈화 (10개 파일)
│   │   ├── profile/       # 프로필 페이지 (4개 파일)
│   │   └── ... (7개 페이지)
│   ├── services/          # 비즈니스 로직
│   │   └── employee-service.js
│   └── utils/             # 유틸리티 함수
│       ├── api.js         # API 호출 래퍼
│       ├── formatting.js
│       └── validation.js
├── images/                # 이미지 리소스
└── uploads/               # 사용자 업로드 파일
```

### 1.2 Flask Static 설정
**위치**: `app/__init__.py:15-17`
```python
app = Flask(__name__,
            template_folder='templates',
            static_folder='static')
```

**특징**:
- 기본 Flask static 폴더 사용 (`/static`)
- url_for('static', filename='...') 패턴 일관되게 사용
- 캐시 버스팅 미적용 (개선 필요)
- CDN 미사용 (외부 리소스: Google Fonts, Font Awesome만 CDN)

### 1.3 url_for 사용 패턴
**검증 결과**: 24개 템플릿 파일에서 104건 사용
- base.html: 30건 (CSS/JS 로딩)
- 페이지별 extra_css 블록: 일관된 패턴
- 모든 정적 파일 참조에 url_for 사용 (하드코딩 없음)

## 2. Template Integration

### 2.1 Base Template 구조 (base.html)
**CSS 로딩 순서** (15-59행):
```html
<!-- 외부 리소스 -->
Google Fonts (Inter), Font Awesome 6.4.0

<!-- Core CSS (순서 중요) -->
1. variables.css    # CSS 변수 정의
2. reset.css        # 브라우저 기본 스타일 초기화
3. theme.css        # 테마 변수

<!-- Layout CSS -->
4. layouts/header.css
5. layouts/sidebar.css
6. layouts/section-nav.css
7. layouts/main-content.css

<!-- Component CSS (27개) -->
8-34. components/*.css

<!-- Page CSS -->
35-36. pages/*.css

<!-- Utilities & Responsive -->
37. utilities.css
38. responsive.css

<!-- 동적 추가 -->
{% block extra_css %}{% endblock %}
```

**JavaScript 로딩** (161-166행):
```html
<!-- 외부 스크립트 -->
Daum 주소 API (동기 로딩)

<!-- 메인 애플리케이션 -->
<script type="module" src="{{ url_for('static', filename='js/app.js') }}"></script>

<!-- 페이지별 스크립트 -->
{% block extra_js %}{% endblock %}
```

### 2.2 조건부 CSS/JS 로딩 패턴
**profile/edit.html 예시** (25-33행):
```html
{% block extra_css %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/layouts/section-nav.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='css/components/card.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='css/pages/employee-form.css') }}">
{% if is_corporate %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/layouts/right-sidebar.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='css/components/tree-selector.css') }}">
{% endif %}
{% endblock %}
```

**장점**:
- 필요한 리소스만 로딩 (조건부 로딩 활용)
- 중복 방지 (base.html에서 공통 리소스 로딩)

**개선점**:
- 일부 페이지에서 이미 base.html에 포함된 CSS 재선언
- 의존성 명시적 관리 부족

## 3. API Integration Points

### 3.1 JavaScript API 호출 패턴
**utils/api.js**: 체계적인 API 래퍼 제공

**기능**:
```javascript
// HTTP 메서드 래퍼
- get(url, params, options)
- post(url, data, options)
- put/patch/del(url, data, options)
- postForm(url, formData, options)  // 파일 업로드용
- uploadFile(url, files, ...)       // 진행률 지원

// 에러 처리
- ApiError 클래스 (status, data 포함)
- handleResponse(): JSON/Text 자동 파싱
- 타임아웃 처리 (기본 30초)

// 유틸리티
- retry(): 재시도 로직 (5xx 에러만)
- cancellableRequest(): 취소 가능한 요청
- downloadFile(): 파일 다운로드
```

**특징**:
- ✅ 일관된 에러 처리
- ✅ 타임아웃 설정
- ✅ AbortController 활용
- ✅ Content-Type 자동 설정
- ⚠️ CSRF 토큰 처리 없음 (개선 필요)

### 3.2 CSRF 토큰 처리 현황
**검증 결과**:
- ❌ JavaScript 파일에서 CSRF 토큰 처리 없음
- ❌ API 요청 헤더에 X-CSRFToken 없음
- ⚠️ Flask-WTF CSRF 활성화 (config.py:74)
  ```python
  WTF_CSRF_ENABLED = True
  ```

**문제점**:
1. HTML 폼 제출만 CSRF 보호 (서버 렌더링)
2. JavaScript fetch 요청은 CSRF 검증 우회 가능
3. API 엔드포인트 보안 취약점

**권장 해결책**:
```javascript
// utils/api.js에 추가
function getCSRFToken() {
    return document.querySelector('meta[name="csrf-token"]')?.content ||
           document.querySelector('input[name="csrf_token"]')?.value;
}

const DEFAULT_HEADERS = {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest',
    'X-CSRFToken': getCSRFToken()  // 추가
};
```

```html
<!-- base.html <head>에 추가 -->
<meta name="csrf-token" content="{{ csrf_token() }}">
```

### 3.3 에러 핸들링 일관성
**현황**:
```javascript
// ✅ 표준화된 에러 클래스 (api.js:18-26)
export class ApiError extends Error {
    constructor(message, status, data = null) {
        super(message);
        this.name = 'ApiError';
        this.status = status;
        this.data = data;
    }
}

// ✅ 응답 처리 로직 (api.js:33-47)
- JSON/Text 자동 파싱
- HTTP 상태 코드 기반 에러 생성
- 상세 에러 데이터 보존

// ⚠️ 사용 패턴 검증 필요
- 13개 파일에서 console.log/error 사용 (총 25건)
- 프로덕션 환경 대비 로깅 전략 필요
```

## 4. Performance Considerations

### 4.1 CSS/JS 로딩 순서 최적화

**현재 구조**:
```html
<head>
  <!-- ✅ 외부 폰트 - preconnect 적용 권장 -->
  <link href="https://fonts.googleapis.com/.." rel="stylesheet">

  <!-- ✅ CSS 순서 최적화됨 -->
  Core → Layout → Components → Pages → Utilities → Responsive

  <!-- ❌ CSS 파일 개수 과다 (38개 파일) -->
  <!-- 번들링 권장: core.min.css, components.min.css, pages.min.css -->
</head>

<body>
  <!-- ✅ 스크립트 하단 배치 -->
  <!-- ✅ ES6 모듈 사용 (type="module") -->
  <script type="module" src="app.js"></script>
</body>
```

**개선 권장사항**:

1. **CSS 번들링** (우선순위: 높음)
   ```
   현재: 38개 CSS 파일 (38 HTTP 요청)
   목표: 3-5개 번들 (개발: 분리, 프로덕션: 결합)

   - core.bundle.css    # variables, reset, theme, utilities, responsive
   - layout.bundle.css  # header, sidebar, section-nav, main-content
   - components.bundle.css  # 모든 컴포넌트
   - pages/[page].css   # 페이지별 필요시만
   ```

2. **JavaScript 모듈 번들링** (우선순위: 중)
   ```
   현재: ES6 모듈 (브라우저 네이티브 로딩)
   장점: 개발 편의성, 캐싱 효율
   단점: HTTP/2 미사용 시 다수 요청

   권장: Rollup/Webpack으로 프로덕션 빌드
   - app.bundle.js (공통 코드)
   - pages/[page].bundle.js (페이지별 코드 스플리팅)
   ```

3. **리소스 힌트 추가** (우선순위: 중)
   ```html
   <head>
     <!-- DNS prefetch -->
     <link rel="dns-prefetch" href="//fonts.googleapis.com">
     <link rel="dns-prefetch" href="//cdnjs.cloudflare.com">

     <!-- Preconnect -->
     <link rel="preconnect" href="https://fonts.googleapis.com">
     <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>

     <!-- Preload critical CSS -->
     <link rel="preload" href="{{ url_for('static', filename='css/core.bundle.css') }}" as="style">
   </head>
   ```

### 4.2 불필요한 파일 로딩 식별

**분석 결과**:

1. **모든 페이지에서 로딩되는 리소스** (base.html)
   ```
   ✅ 적절: variables, reset, theme, header, sidebar, button, badge, alert
   ⚠️ 검토 필요:
   - components/salary-*.css (3개 파일) → 급여 페이지만 필요
   - components/contract.css → 계약 페이지만 필요
   - components/data-table-advanced.css → 목록 페이지만 필요
   - components/tree-selector.css → 조직도 페이지만 필요
   ```

2. **권장 분리 전략**:
   ```html
   <!-- base.html: 공통 필수만 -->
   <link rel="stylesheet" href="core.bundle.css">
   <link rel="stylesheet" href="layout.bundle.css">
   <link rel="stylesheet" href="common-components.bundle.css">
   <!-- button, badge, alert, forms, table, modal만 -->

   <!-- 페이지별 extra_css -->
   {% block extra_css %}
     <!-- 특화 컴포넌트만 로딩 -->
   {% endblock %}
   ```

3. **JavaScript 최적화**:
   ```javascript
   // app.js: 전역 네임스페이스만
   - HRApp.toast
   - HRApp.filter
   - HRApp.ui (기본 유틸리티)

   // 페이지별 동적 임포트
   if (document.getElementById('salaryCalculator')) {
       import('./components/salary-calculator.js')
           .then(module => module.init());
   }
   ```

### 4.3 번들링/최소화 전략

**현재 상태**:
- ❌ 번들링 없음 (개발 구조 그대로 프로덕션)
- ❌ 최소화(minification) 없음
- ❌ 소스맵 없음
- ⚠️ ES6 모듈 브라우저 네이티브 로딩 (HTTP/2 필요)

**권장 빌드 파이프라인**:

```javascript
// package.json (새로 추가)
{
  "scripts": {
    "build:css": "postcss app/static/css/**/*.css --dir dist/css --use cssnano autoprefixer",
    "build:js": "rollup -c rollup.config.js",
    "build": "npm run build:css && npm run build:js",
    "watch": "npm run build:css -- --watch & npm run build:js -- --watch"
  },
  "devDependencies": {
    "rollup": "^3.x",
    "@rollup/plugin-terser": "^0.4.x",
    "postcss-cli": "^10.x",
    "cssnano": "^6.x",
    "autoprefixer": "^10.x"
  }
}

// rollup.config.js
export default {
  input: {
    app: 'app/static/js/app.js',
    'pages/employee': 'app/static/js/pages/employee/index.js',
    'pages/profile': 'app/static/js/pages/profile/profile-navigation.js'
  },
  output: {
    dir: 'app/static/dist/js',
    format: 'es',
    entryFileNames: '[name].[hash].js',
    chunkFileNames: 'chunks/[name].[hash].js',
    sourcemap: true
  },
  plugins: [
    terser(),
    // 코드 스플리팅 자동 처리
  ]
};
```

**Flask 통합**:
```python
# config.py에 추가
class ProductionConfig(Config):
    # 정적 파일 버전 관리
    STATIC_VERSION = os.environ.get('STATIC_VERSION', 'v1.0.0')

    @staticmethod
    def versioned_url_for(endpoint, **values):
        if endpoint == 'static':
            filename = values.get('filename')
            if filename:
                values['v'] = ProductionConfig.STATIC_VERSION
        return url_for(endpoint, **values)
```

## 5. Security Aspects

### 5.1 XSS 방지 패턴

**Jinja2 자동 이스케이핑**: ✅ 활성화됨
```python
# Flask 기본 설정으로 자동 활성화
# 모든 {{ variable }} 출력은 HTML 이스케이프됨
```

**JavaScript 컨텍스트 보안**:
```javascript
// ❌ 발견된 취약점 없음
// ✅ DOM 조작 시 textContent/createElement 사용
// ✅ innerHTML 직접 사용 최소화

// 예시: pages/employee/templates.js
export function getEducationTemplate(index) {
    const div = document.createElement('div');
    div.className = 'dynamic-section';
    div.innerHTML = `...`;  // 정적 템플릿만, 사용자 입력 없음
    return div;
}
```

**검증 필요 영역**:
1. `components/toast.js` - 메시지 출력
2. `components/data-table/cell-renderer.js` - 동적 셀 렌더링

**권장 개선**:
```javascript
// components/toast.js
function showToast(message, type = 'info') {
    const messageEl = document.createElement('span');
    messageEl.textContent = message;  // ✅ textContent 사용
    // messageEl.innerHTML = message;  // ❌ 금지

    toastEl.appendChild(messageEl);
}
```

### 5.2 사용자 입력 처리 안전성

**폼 데이터 전송**:
```javascript
// ✅ API 래퍼가 JSON 자동 변환
// ✅ Content-Type 명시
export async function post(url, data = {}, options = {}) {
    return request(url, {
        method: 'POST',
        body: data,  // JSON.stringify 자동 처리
        ...options
    });
}

// ✅ 파일 업로드 안전 처리
export async function postForm(url, formData, options = {}) {
    const formHeaders = { ...headers };
    delete formHeaders['Content-Type'];  // 브라우저 자동 설정
    return request(url, {
        method: 'POST',
        headers: formHeaders,
        body: formData,  // FormData 그대로 전송
        ...rest
    });
}
```

**입력 검증**:
```javascript
// components/form-validator.js 존재
// ⚠️ 검증 내용 확인 필요

// 권장 패턴
function sanitizeInput(input) {
    return input
        .trim()
        .replace(/[<>]/g, '')  // 기본적인 XSS 방지
        .substring(0, 255);    // 길이 제한
}
```

### 5.3 외부 리소스 로딩 보안

**CDN 리소스** (base.html):
```html
<!-- ✅ SRI(Subresource Integrity) 미적용 - 개선 필요 -->
<link rel="stylesheet"
      href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

<!-- ✅ 권장 개선 -->
<link rel="stylesheet"
      href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
      integrity="sha512-iecdLmaskl7CVkqkXNQ/ZH/XLlvWZOJyj7Yy7tcenmpD1ypASozpmT/E0iPtmFIB46ZmdtAc9eNBvH0H/ZpiBw=="
      crossorigin="anonymous"
      referrerpolicy="no-referrer">
```

**외부 스크립트**:
```html
<!-- Daum 주소 API -->
<script src="//t1.daumcdn.net/mapjsapi/bundle/postcode/prod/postcode.v2.js"></script>

<!-- ✅ 권장 개선 -->
<script src="//t1.daumcdn.net/mapjsapi/bundle/postcode/prod/postcode.v2.js"
        crossorigin="anonymous"></script>
```

**CSP(Content Security Policy) 권장**:
```python
# app/__init__.py 또는 미들웨어
@app.after_request
def set_security_headers(response):
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' https://t1.daumcdn.net; "
        "style-src 'self' https://fonts.googleapis.com https://cdnjs.cloudflare.com; "
        "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
        "img-src 'self' data:; "
    )
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response
```

## 6. 백엔드 관점 개선 권장사항

### 6.1 우선순위: 높음 (보안)

1. **CSRF 토큰 통합**
   ```python
   # app/__init__.py
   from flask_wtf.csrf import CSRFProtect
   csrf = CSRFProtect()
   csrf.init_app(app)

   # 모든 AJAX 요청에 CSRF 토큰 포함
   ```

   ```javascript
   // utils/api.js
   const DEFAULT_HEADERS = {
       'X-CSRFToken': getCSRFToken()
   };
   ```

2. **보안 헤더 추가**
   - CSP(Content Security Policy)
   - X-Content-Type-Options
   - X-Frame-Options
   - Referrer-Policy

3. **외부 리소스 SRI 적용**
   - Font Awesome
   - Google Fonts
   - Daum 주소 API

### 6.2 우선순위: 중 (성능)

1. **정적 파일 캐시 버스팅**
   ```python
   # config.py
   STATIC_VERSION = os.environ.get('STATIC_VERSION', datetime.now().strftime('%Y%m%d%H%M'))

   # 템플릿 헬퍼
   def versioned_static(filename):
       return url_for('static', filename=filename, v=STATIC_VERSION)
   ```

2. **CSS/JS 번들링 파이프라인 구축**
   - 개발 환경: 분리된 파일 (디버깅 용이)
   - 프로덕션: 번들링 + 최소화
   - Flask 환경 변수로 전환

3. **HTTP/2 또는 HTTP/3 지원 확인**
   - Nginx/Apache 설정 검증
   - 다중 리소스 로딩 최적화

### 6.3 우선순위: 중-낮 (아키텍처)

1. **정적 파일 CDN 분리**
   ```python
   # config.py
   class ProductionConfig(Config):
       STATIC_URL = os.environ.get('CDN_URL', '/static')

   # 템플릿
   {{ cdn_url_for('static', filename='css/core.css') }}
   ```

2. **조건부 리소스 로딩 자동화**
   ```python
   # 템플릿 헬퍼
   @app.context_processor
   def inject_page_resources():
       page_css = {
           'profile.edit': ['section-nav.css', 'employee-form.css'],
           'employees.list': ['data-table-advanced.css'],
       }
       return {'page_css': page_css}
   ```

3. **개발/프로덕션 환경 분리**
   ```python
   # config.py
   class DevelopmentConfig(Config):
       USE_BUNDLED_ASSETS = False
       DEBUG_TB_INTERCEPT_REDIRECTS = False

   class ProductionConfig(Config):
       USE_BUNDLED_ASSETS = True
       COMPRESS_MIMETYPES = ['text/css', 'application/javascript']
   ```

### 6.4 우선순위: 낮 (최적화)

1. **리소스 프리로딩 전략**
   - Critical CSS 인라인화
   - 폰트 preload
   - 이미지 lazy loading

2. **Service Worker 도입 (PWA)**
   - 오프라인 지원
   - 정적 리소스 캐싱
   - 백그라운드 동기화

3. **모니터링 및 성능 측정**
   - 정적 파일 로딩 시간 측정
   - 사용자 경험 메트릭 (LCP, FID, CLS)
   - 에러 추적 (Sentry 등)

## 7. 체크리스트

### 보안
- [ ] CSRF 토큰 JavaScript 통합
- [ ] 보안 헤더 설정 (CSP, X-Frame-Options 등)
- [ ] 외부 리소스 SRI 적용
- [ ] XSS 방지 패턴 검증 (toast, data-table)
- [ ] API 엔드포인트 인증/인가 검증

### 성능
- [ ] CSS 번들링 (38개 → 3-5개)
- [ ] JavaScript 번들링 (페이지별 스플리팅)
- [ ] 캐시 버스팅 전략 구현
- [ ] HTTP/2 지원 확인
- [ ] 불필요한 전역 CSS 제거

### 아키텍처
- [ ] 개발/프로덕션 빌드 분리
- [ ] 정적 파일 버전 관리
- [ ] CDN 전략 수립
- [ ] 리소스 프리로딩 최적화

### 코드 품질
- [ ] console.log 제거 (프로덕션)
- [ ] 에러 로깅 전략 수립
- [ ] API 호출 재시도 정책 검토
- [ ] 파일 업로드 보안 검증

## 8. 구현 예시

### CSRF 토큰 통합 (전체 솔루션)

**1단계: 템플릿에 메타 태그 추가**
```html
<!-- app/templates/base.html <head> 내부 -->
<meta name="csrf-token" content="{{ csrf_token() }}">
```

**2단계: API 유틸리티 업데이트**
```javascript
// app/static/js/utils/api.js
/**
 * CSRF 토큰 가져오기
 */
function getCSRFToken() {
    // 1. 메타 태그에서 확인
    const metaToken = document.querySelector('meta[name="csrf-token"]')?.content;
    if (metaToken) return metaToken;

    // 2. 폼 input에서 확인 (fallback)
    const inputToken = document.querySelector('input[name="csrf_token"]')?.value;
    if (inputToken) return inputToken;

    console.warn('CSRF token not found');
    return '';
}

const DEFAULT_HEADERS = {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest',
    'X-CSRFToken': getCSRFToken()  // 추가
};

// FormData 전송 시에도 CSRF 토큰 자동 추가
export async function postForm(url, formData, options = {}) {
    const { headers = {}, ...rest } = options;

    const formHeaders = { ...headers };
    delete formHeaders['Content-Type'];

    // CSRF 토큰 추가
    formHeaders['X-CSRFToken'] = getCSRFToken();

    return request(url, {
        method: 'POST',
        headers: formHeaders,
        body: formData,
        ...rest
    });
}
```

**3단계: Flask CSRF 설정 확인**
```python
# app/config.py - 이미 활성화됨
WTF_CSRF_ENABLED = True

# app/blueprints/api.py - API 라우트에서 검증
from flask_wtf.csrf import validate_csrf
from werkzeug.exceptions import BadRequest

@api_bp.route('/employees/<int:employee_id>', methods=['PUT'])
def update_employee(employee_id):
    # AJAX 요청 CSRF 검증
    try:
        validate_csrf(request.headers.get('X-CSRFToken'))
    except:
        return jsonify({'error': 'CSRF validation failed'}), 400

    # 기존 로직
    ...
```

### 정적 파일 번들링 (빌드 시스템)

**1단계: package.json 생성**
```json
{
  "name": "hrmanagement-static",
  "private": true,
  "scripts": {
    "build:css": "postcss app/static/css/bundles/*.css --dir app/static/dist/css --use cssnano autoprefixer",
    "build:js": "rollup -c",
    "build": "npm run build:css && npm run build:js",
    "watch": "npm run build -- --watch",
    "clean": "rm -rf app/static/dist"
  },
  "devDependencies": {
    "rollup": "^4.0.0",
    "@rollup/plugin-terser": "^0.4.0",
    "postcss-cli": "^11.0.0",
    "cssnano": "^6.0.0",
    "autoprefixer": "^10.4.0"
  }
}
```

**2단계: CSS 번들 정의**
```css
/* app/static/css/bundles/core.css */
@import '../core/variables.css';
@import '../core/reset.css';
@import '../core/theme.css';
@import '../core/utilities.css';
@import '../core/responsive.css';

/* app/static/css/bundles/layout.css */
@import '../layouts/header.css';
@import '../layouts/sidebar.css';
@import '../layouts/section-nav.css';
@import '../layouts/main-content.css';

/* app/static/css/bundles/components.css */
@import '../components/button.css';
@import '../components/badge.css';
@import '../components/alert.css';
@import '../components/forms.css';
@import '../components/modal.css';
/* ... 공통 컴포넌트만 */
```

**3단계: Rollup 설정**
```javascript
// rollup.config.js
import { terser } from '@rollup/plugin-terser';

export default {
  input: {
    app: 'app/static/js/app.js',
    'employee-form': 'app/static/js/pages/employee/index.js',
    'profile': 'app/static/js/pages/profile/profile-navigation.js'
  },
  output: {
    dir: 'app/static/dist/js',
    format: 'es',
    sourcemap: true,
    entryFileNames: '[name].[hash].js',
    chunkFileNames: 'chunks/[name].[hash].js'
  },
  plugins: [
    terser({
      compress: {
        drop_console: true  // 프로덕션에서 console 제거
      }
    })
  ]
};
```

**4단계: Flask 환경별 템플릿 헬퍼**
```python
# app/utils/template_helpers.py
import os
import json

def register_template_utils(app):
    # 빌드 매니페스트 로드 (해시 파일명 매핑)
    manifest_path = os.path.join(app.static_folder, 'dist', 'manifest.json')
    manifest = {}
    if os.path.exists(manifest_path):
        with open(manifest_path) as f:
            manifest = json.load(f)

    @app.context_processor
    def inject_static_helpers():
        def static_url(filename):
            """환경에 따라 원본 또는 번들 파일 반환"""
            if app.config.get('USE_BUNDLED_ASSETS'):
                # 프로덕션: 번들 파일 (해시 포함)
                bundled = manifest.get(filename, filename)
                return url_for('static', filename=f'dist/{bundled}')
            else:
                # 개발: 원본 파일
                return url_for('static', filename=filename)

        return {'static_url': static_url}
```

**5단계: 템플릿 업데이트**
```html
<!-- base.html -->
{% if config.USE_BUNDLED_ASSETS %}
  <!-- 프로덕션: 번들 -->
  <link rel="stylesheet" href="{{ static_url('css/core.css') }}">
  <link rel="stylesheet" href="{{ static_url('css/layout.css') }}">
  <link rel="stylesheet" href="{{ static_url('css/components.css') }}">
{% else %}
  <!-- 개발: 개별 파일 -->
  <link rel="stylesheet" href="{{ url_for('static', filename='css/core/variables.css') }}">
  <!-- ... 기존 개별 파일들 ... -->
{% endif %}
```

## 9. 결론

### 강점
1. ✅ 체계적인 모듈화 구조 (CSS/JS 분리)
2. ✅ url_for 일관된 사용
3. ✅ ES6 모듈 기반 JavaScript 아키텍처
4. ✅ API 래퍼 표준화 (utils/api.js)
5. ✅ 컴포넌트 재사용성 높음

### 주요 개선 필요 영역
1. 🔴 CSRF 토큰 JavaScript 통합 (보안 취약점)
2. 🟡 CSS/JS 번들링 (성능 최적화)
3. 🟡 캐시 버스팅 전략 (배포 전략)
4. 🟡 외부 리소스 SRI 적용 (보안)
5. 🟢 console.log 제거 (프로덕션 준비)

### 우선 조치 항목
1. CSRF 토큰 통합 (1-2일)
2. 보안 헤더 설정 (1일)
3. 빌드 시스템 구축 (3-5일)
4. 성능 모니터링 도구 도입 (2-3일)
