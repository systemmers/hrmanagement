# 인사카드 관리 시스템

Flask 기반의 직원 정보 통합 관리 시스템입니다.

## 주요 기능

- 관리자 인증 및 로그인/로그아웃
- 직원 정보 등록, 조회, 수정, 삭제 (CRUD)
- 직원 검색 및 필터링
- 대시보드 통계 (총 직원 수, 활성 직원, 대기 중, 만료 예정)
- 프로필 사진 업로드
- 반응형 UI 디자인

## 기술 스택

### Backend
- **Python 3.12+**
- **Flask 3.1.0** - 웹 프레임워크
- **Flask-SQLAlchemy** - ORM
- **Flask-Login** - 인증
- **Flask-WTF** - 폼 처리 및 CSRF 보호
- **Flask-Migrate** - 데이터베이스 마이그레이션

### Frontend
- **Jinja2** - 템플릿 엔진
- **CSS Variables** - 디자인 토큰
- **Vanilla JavaScript** - 클라이언트 사이드 로직
- **Font Awesome 6.4.0** - 아이콘
- **Inter Font** - 타이포그래피

### Database
- **SQLite** - 개발용 데이터베이스

## 프로젝트 구조

```
insacard/
├── app/
│   ├── __init__.py              # 앱 팩토리 및 확장 초기화
│   ├── models.py                # 데이터베이스 모델
│   ├── auth/                    # 인증 블루프린트
│   │   ├── __init__.py
│   │   ├── routes.py            # 로그인/로그아웃 라우트
│   │   └── forms.py             # 로그인 폼
│   ├── employee/                # 직원 관리 블루프린트
│   │   ├── __init__.py
│   │   ├── routes.py            # CRUD 라우트
│   │   └── forms.py             # 직원 폼
│   ├── api/                     # REST API 블루프린트
│   │   ├── __init__.py
│   │   └── routes.py            # 검색/통계 API
│   ├── templates/               # Jinja2 템플릿
│   │   ├── base.html            # 기본 레이아웃
│   │   ├── auth/
│   │   │   └── login.html       # 로그인 페이지
│   │   └── employee/
│   │       ├── index.html       # 대시보드
│   │       ├── detail.html      # 직원 상세
│   │       ├── register.html    # 직원 등록
│   │       └── edit.html        # 직원 수정
│   └── static/                  # 정적 파일
│       ├── css/
│       │   └── style.css        # 메인 스타일시트
│       ├── js/
│       │   └── main.js          # 메인 JavaScript
│       └── uploads/             # 업로드 파일
│           └── employees/       # 직원 사진
├── scripts/
│   ├── init_db.py              # 데이터베이스 초기화
│   └── seed_data.py            # 샘플 데이터 생성
├── config.py                   # 설정 클래스
├── run.py                      # 애플리케이션 엔트리 포인트
├── requirements.txt            # Python 패키지 의존성
└── .env                        # 환경 변수

```

## 설치 방법

### 1. 저장소 클론

```bash
git clone <repository-url>
cd insacard
```

### 2. 가상 환경 생성 및 활성화

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. 의존성 설치

```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정

`.env` 파일이 이미 설정되어 있습니다. 프로덕션 환경에서는 `SECRET_KEY`를 반드시 변경하세요.

```bash
# .env
FLASK_APP=run.py
FLASK_DEBUG=1
SECRET_KEY=dev-insacard-secret-key-2025
DATABASE_URL=sqlite:///insacard_dev.db
```

### 5. 데이터베이스 초기화

```bash
python3 scripts/init_db.py
```

이 명령은 다음을 수행합니다:
- 데이터베이스 테이블 생성
- 관리자 계정 생성 (username: `admin`, password: `admin123!`)
- 부서 마스터 데이터 생성 (5개)
- 직급 마스터 데이터 생성 (5개)

### 6. 샘플 데이터 생성 (선택사항)

```bash
python3 scripts/seed_data.py
```

25명의 샘플 직원 데이터가 생성됩니다.

### 7. 애플리케이션 실행

**방법 1: 시작 스크립트 사용 (권장)**

```bash
./start.sh
```

**방법 2: 수동 실행**

```bash
source venv/bin/activate  # 가상환경 활성화
python3 run.py
```

애플리케이션이 http://localhost:5001 에서 실행됩니다.

**중요**: 반드시 가상환경(venv)을 활성화한 상태에서 실행해야 합니다.

## 기본 계정

### 관리자 계정
- **아이디**: `admin`
- **비밀번호**: `admin123!`

## API 엔드포인트

### 인증
- `GET /auth/login` - 로그인 페이지
- `POST /auth/login` - 로그인 처리
- `GET /auth/logout` - 로그아웃

### 직원 관리
- `GET /` - 대시보드 (직원 목록)
- `GET /employee/new` - 직원 등록 폼
- `POST /employee/new` - 직원 등록 처리
- `GET /employee/<id>` - 직원 상세 조회
- `GET /employee/<id>/edit` - 직원 수정 폼
- `POST /employee/<id>/edit` - 직원 수정 처리
- `POST /employee/<id>/delete` - 직원 삭제

### REST API
- `GET /api/employees` - 직원 목록 조회 (검색/필터 지원)
- `GET /api/employees/<id>` - 직원 상세 조회
- `GET /api/statistics` - 대시보드 통계

## 주요 기능 설명

### 1. 대시보드
- 직원 수 통계 (총 직원, 활성, 대기 중, 만료 예정)
- 직원 카드 그리드 뷰
- 실시간 검색 기능

### 2. 직원 관리
- **등록**: 이름, 전화번호, 이메일, 주소, 부서, 직급, 입사일, 고용형태, 근무지, 상태, 사진
- **조회**: 직원 상세 정보 및 사진 표시
- **수정**: 모든 필드 수정 가능
- **삭제**: 직원 삭제 (확인 후)

### 3. 검색 기능
- 이름, 부서, 직급으로 실시간 검색
- 디바운싱을 통한 성능 최적화

### 4. 파일 업로드
- 프로필 사진 업로드
- 지원 형식: PNG, JPG, JPEG, GIF
- 최대 크기: 5MB
- UUID 기반 파일명 생성

## 디자인 시스템

### 컬러 팔레트
- 15단계 그레이스케일 (50-950)
- Pure White (#FFFFFF)
- 시스템 색상 (Success, Warning, Error)

### 타이포그래피
- Font Family: Inter
- Font Weights: 200-700
- Font Sizes: 0.75rem - 3rem

### 스페이싱
- 0.5rem - 20rem (2px - 320px)

### Border Radius
- sm: 0.25rem
- md: 0.5rem
- lg: 0.75rem
- xl: 1rem

## 개발 가이드

### 새로운 기능 추가

1. **모델 수정**: `app/models.py`에서 데이터베이스 모델 수정
2. **마이그레이션**: `flask db migrate -m "메시지"` 및 `flask db upgrade`
3. **블루프린트**: 해당 블루프린트의 `routes.py`에 라우트 추가
4. **폼**: `forms.py`에 WTForms 폼 클래스 추가
5. **템플릿**: `app/templates/`에 Jinja2 템플릿 추가
6. **스타일**: `app/static/css/style.css`에 CSS 추가

### 코드 스타일
- Python: PEP 8
- JavaScript: ES6+
- CSS: BEM 명명 규칙

## 트러블슈팅

### 포트 충돌
5000 포트가 사용 중인 경우:
```bash
lsof -ti:5000 | xargs kill -9
```

### 데이터베이스 리셋
```bash
rm insacard_dev.db
python3 scripts/init_db.py
```

### 의존성 문제
```bash
pip install --upgrade -r requirements.txt
```

## 라이선스

이 프로젝트는 개발 및 학습 목적으로 작성되었습니다.

## 문의

프로젝트 관련 문의사항이 있으시면 이슈를 등록해주세요.
