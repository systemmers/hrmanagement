# API 명세서

인사카드 관리 시스템 REST API 문서입니다.

## 기본 정보

- **Base URL**: `http://localhost:5000`
- **Content-Type**: `application/json`
- **인증 방식**: Session-based (Flask-Login)
- **CSRF 보호**: 활성화 (POST/PUT/DELETE 요청 시 CSRF 토큰 필요)

## 인증 API

### 1. 로그인

관리자 계정으로 로그인합니다.

**Endpoint**
```
POST /auth/login
```

**Request Body** (Form Data)
```json
{
  "username": "admin",
  "password": "admin123!",
  "remember_me": false
}
```

**Response**
```
302 Redirect to /
Set-Cookie: session=...
```

**Success Response**
- Status: 302 (Redirect)
- Location: `/` (대시보드)
- Flash Message: `{username}님, 환영합니다!` (success)

**Error Response**
- Status: 200 (페이지 재표시)
- Flash Message: `아이디 또는 비밀번호가 올바르지 않습니다.` (danger)

### 2. 로그아웃

현재 세션을 종료합니다.

**Endpoint**
```
GET /auth/logout
```

**Response**
```
302 Redirect to /auth/login
```

**Success Response**
- Status: 302 (Redirect)
- Location: `/auth/login`
- Flash Message: `로그아웃되었습니다.` (info)

## 직원 관리 API (Web UI)

### 1. 대시보드

직원 목록과 통계를 표시합니다.

**Endpoint**
```
GET /
```

**Authentication**: Required

**Response**
- Status: 200
- Content-Type: text/html
- Template: `employee/index.html`

**Template Context**
```python
{
  "employees": [Employee],  # 직원 목록
  "total_count": int,       # 총 직원 수
  "active_count": int,      # 활성 직원 수
  "warning_count": int,     # 대기 중 직원 수
  "expired_count": int      # 만료 예정 직원 수
}
```

### 2. 직원 등록

새로운 직원을 등록합니다.

**Endpoint**
```
GET /employee/new
POST /employee/new
```

**Authentication**: Required

**GET Response**
- Status: 200
- Content-Type: text/html
- Template: `employee/register.html`

**POST Request** (Multipart Form Data)
```
name: string (required)
phone: string
email: string
address: string
department_id: integer
position_id: integer
hire_date: date
employment_type: string
workplace: string
status: string (active|warning|expired)
photo: file (image/png, image/jpeg, image/jpg, image/gif, max 5MB)
```

**POST Success Response**
- Status: 302 (Redirect)
- Location: `/employee/{id}`
- Flash Message: `직원이 등록되었습니다.` (success)

**POST Error Response**
- Status: 200 (페이지 재표시)
- Flash Message: 유효성 검사 오류 메시지 (danger)

### 3. 직원 상세 조회

특정 직원의 상세 정보를 조회합니다.

**Endpoint**
```
GET /employee/{id}
```

**Authentication**: Required

**Parameters**
- `id` (path): 직원 ID (integer)

**Response**
- Status: 200
- Content-Type: text/html
- Template: `employee/detail.html`

**Template Context**
```python
{
  "employee": Employee  # 직원 객체
}
```

**Error Response**
- Status: 404
- Error: `직원을 찾을 수 없습니다.`

### 4. 직원 수정

직원 정보를 수정합니다.

**Endpoint**
```
GET /employee/{id}/edit
POST /employee/{id}/edit
```

**Authentication**: Required

**Parameters**
- `id` (path): 직원 ID (integer)

**GET Response**
- Status: 200
- Content-Type: text/html
- Template: `employee/edit.html`

**POST Request** (Multipart Form Data)
```
name: string (required)
phone: string
email: string
address: string
department_id: integer
position_id: integer
hire_date: date
employment_type: string
workplace: string
status: string (active|warning|expired)
photo: file (선택사항)
```

**POST Success Response**
- Status: 302 (Redirect)
- Location: `/employee/{id}`
- Flash Message: `직원 정보가 수정되었습니다.` (success)

**POST Error Response**
- Status: 200 (페이지 재표시)
- Flash Message: 유효성 검사 오류 메시지 (danger)

### 5. 직원 삭제

직원을 삭제합니다.

**Endpoint**
```
POST /employee/{id}/delete
```

**Authentication**: Required

**Parameters**
- `id` (path): 직원 ID (integer)

**Success Response**
- Status: 302 (Redirect)
- Location: `/`
- Flash Message: `직원이 삭제되었습니다.` (success)

**Error Response**
- Status: 404
- Flash Message: `직원을 찾을 수 없습니다.` (danger)

## REST API

### 1. 직원 목록 조회

직원 목록을 JSON 형식으로 조회합니다. 검색 및 필터링을 지원합니다.

**Endpoint**
```
GET /api/employees
```

**Authentication**: Required

**Query Parameters**
- `q` (optional): 검색어 (이름, 전화번호, 이메일로 검색)
- `status` (optional): 상태 필터 (active, warning, expired)
- `department_id` (optional): 부서 ID 필터
- `position_id` (optional): 직급 ID 필터

**Examples**
```
GET /api/employees
GET /api/employees?q=김철수
GET /api/employees?status=active
GET /api/employees?department_id=1&position_id=3
```

**Success Response**
```json
{
  "success": true,
  "employees": [
    {
      "id": 1,
      "name": "김철수",
      "phone": "010-1234-5678",
      "email": "kim@example.com",
      "department": "개발팀",
      "position": "과장",
      "status": "active",
      "hire_date": "2020-01-15",
      "photo": "employees/abc123.jpg",
      "address": "서울시 강남구",
      "employment_type": "정규직",
      "workplace": "본사",
      "created_at": "2025-11-19T10:00:00"
    }
  ],
  "count": 25
}
```

**Error Response**
```json
{
  "success": false,
  "message": "오류 메시지"
}
```

### 2. 직원 상세 조회

특정 직원의 상세 정보를 JSON 형식으로 조회합니다.

**Endpoint**
```
GET /api/employees/{id}
```

**Authentication**: Required

**Parameters**
- `id` (path): 직원 ID (integer)

**Example**
```
GET /api/employees/1
```

**Success Response**
```json
{
  "success": true,
  "employee": {
    "id": 1,
    "name": "김철수",
    "phone": "010-1234-5678",
    "email": "kim@example.com",
    "department": "개발팀",
    "department_id": 1,
    "position": "과장",
    "position_id": 3,
    "status": "active",
    "hire_date": "2020-01-15",
    "photo": "employees/abc123.jpg",
    "address": "서울시 강남구",
    "employment_type": "정규직",
    "workplace": "본사",
    "created_at": "2025-11-19T10:00:00",
    "updated_at": "2025-11-19T12:00:00"
  }
}
```

**Error Response**
```json
{
  "success": false,
  "message": "직원을 찾을 수 없습니다."
}
```

### 3. 대시보드 통계

대시보드에 표시할 통계 정보를 조회합니다.

**Endpoint**
```
GET /api/statistics
```

**Authentication**: Required

**Success Response**
```json
{
  "success": true,
  "statistics": {
    "total_count": 25,
    "active_count": 20,
    "warning_count": 3,
    "expired_count": 2,
    "by_department": {
      "개발팀": 8,
      "디자인팀": 5,
      "마케팅팀": 6,
      "영업팀": 4,
      "관리팀": 2
    },
    "by_position": {
      "사원": 10,
      "대리": 7,
      "과장": 5,
      "차장": 2,
      "부장": 1
    }
  }
}
```

**Error Response**
```json
{
  "success": false,
  "message": "오류 메시지"
}
```

## 데이터 모델

### Employee (직원)
```python
{
  "id": integer,                    # 고유 ID
  "name": string,                   # 이름 (필수)
  "phone": string,                  # 전화번호
  "email": string,                  # 이메일
  "address": string,                # 주소
  "department_id": integer,         # 부서 ID (외래키)
  "department": string,             # 부서 이름
  "position_id": integer,           # 직급 ID (외래키)
  "position": string,               # 직급 이름
  "hire_date": date,                # 입사일
  "employment_type": string,        # 고용형태
  "workplace": string,              # 근무지
  "status": string,                 # 상태 (active, warning, expired)
  "photo": string,                  # 사진 파일명
  "created_at": datetime,           # 등록일시
  "updated_at": datetime            # 수정일시
}
```

### Department (부서)
```python
{
  "id": integer,         # 고유 ID
  "name": string,        # 부서 이름
  "created_at": datetime # 등록일시
}
```

### Position (직급)
```python
{
  "id": integer,         # 고유 ID
  "name": string,        # 직급 이름
  "level": integer,      # 직급 레벨 (1-5)
  "created_at": datetime # 등록일시
}
```

### User (관리자)
```python
{
  "id": integer,            # 고유 ID
  "username": string,       # 아이디 (고유)
  "password_hash": string,  # 비밀번호 해시
  "name": string,           # 이름
  "created_at": datetime    # 등록일시
}
```

## 상태 코드

| 코드 | 설명 |
|-----|-----|
| 200 | 성공 |
| 302 | 리다이렉트 |
| 400 | 잘못된 요청 |
| 401 | 인증 필요 |
| 403 | 권한 없음 |
| 404 | 리소스 없음 |
| 500 | 서버 오류 |

## CSRF 보호

POST, PUT, DELETE 요청 시 CSRF 토큰이 필요합니다.

### HTML Form
```html
<form method="POST">
  {{ form.hidden_tag() }}
  <!-- 폼 필드 -->
</form>
```

### AJAX Request
```javascript
fetch('/api/employees', {
  method: 'POST',
  headers: {
    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(data)
})
```

## 에러 처리

### Flash Messages
페이지 리다이렉트 시 플래시 메시지로 결과를 전달합니다.

**카테고리**
- `success`: 성공 메시지 (녹색)
- `danger`: 오류 메시지 (빨간색)
- `warning`: 경고 메시지 (노란색)
- `info`: 정보 메시지 (파란색)

### JSON Error Response
API 엔드포인트에서는 JSON 형식으로 오류를 반환합니다.

```json
{
  "success": false,
  "message": "오류 메시지",
  "errors": {
    "field_name": ["오류 상세 메시지"]
  }
}
```

## 파일 업로드

### 허용 파일 형식
- PNG (.png)
- JPEG (.jpg, .jpeg)
- GIF (.gif)

### 최대 파일 크기
- 5MB

### 저장 경로
- `app/static/uploads/employees/{uuid}.{ext}`

### 파일명 규칙
- UUID v4 기반 고유 파일명 생성
- 원본 확장자 유지

## 보안

### 인증
- Flask-Login을 사용한 세션 기반 인증
- 비밀번호는 Werkzeug의 `pbkdf2:sha256`으로 해싱

### CSRF 보호
- Flask-WTF의 CSRFProtect 사용
- 모든 상태 변경 요청에 CSRF 토큰 검증

### 파일 업로드 보안
- `secure_filename`을 사용한 안전한 파일명 생성
- UUID 기반 파일명으로 충돌 방지
- 허용된 확장자만 업로드 가능

## 제한사항

### 현재 버전 (Phase 1 MVP)
- 관리자 인증만 지원 (직원 로그인 미지원)
- PDF 출력 기능 미지원 (Phase 2 예정)
- 파일 첨부 관리 미지원
- 페이지네이션 미구현
- API Rate Limiting 미구현

## 향후 개선 사항

### Phase 2
- PDF 출력 기능
- 직원별 로그인 및 권한 관리
- 파일 첨부 관리
- 페이지네이션
- 고급 검색 및 필터링
- API Rate Limiting
- 감사 로그 (Audit Log)
