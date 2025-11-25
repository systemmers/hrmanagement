# 인사카드 관리 시스템 - Flask MVP

Flask 기반의 인사카드 관리 시스템 MVP(Minimum Viable Product) 버전입니다.

## 프로젝트 개요

직원 정보를 효율적으로 관리하기 위한 웹 기반 시스템입니다. 직원 등록, 조회, 수정, 삭제 등의 기본 CRUD 기능을 제공합니다.

## 주요 기능

### 직원 관리 (CRUD)
- 직원 등록
- 직원 목록 조회
- 직원 상세 정보 조회
- 직원 정보 수정
- 직원 삭제

### 검색 및 필터링
- 이름, 부서, 직급으로 검색
- 재직 상태별 필터링 (정상, 대기, 만료)

### 대시보드
- 통계 정보 표시 (총 직원, 활성, 대기, 만료)
- 직원 카드 그리드 뷰
- 직원 테이블 뷰

## 기술 스택

### Backend
- **Flask 3.0**: 웹 프레임워크
- **Flask-WTF**: 폼 처리 및 유효성 검증
- **Python 3.8+**: 프로그래밍 언어

### Frontend
- **Jinja2**: 템플릿 엔진
- **HTML5/CSS3**: 마크업 및 스타일
- **Vanilla JavaScript**: 클라이언트 사이드 스크립트
- **Font Awesome 6.4**: 아이콘
- **Google Fonts (Inter)**: 타이포그래피

### 데이터 저장
- **JSON 파일**: 임시 데이터 저장 (MVP용)
- 추후 SQLite/PostgreSQL로 전환 가능한 구조

## 프로젝트 구조

```
insacard/
├── app.py                      # Flask 애플리케이션 메인
├── config.py                   # 설정 파일
├── models.py                   # 데이터 모델
├── forms.py                    # WTForms 폼
├── requirements.txt            # 의존성 패키지
├── README.md                   # 프로젝트 문서
├── templates/                  # Jinja2 템플릿
│   ├── base.html              # 기본 레이아웃
│   ├── index.html             # 대시보드
│   ├── employee_list.html     # 직원 목록
│   ├── employee_detail.html   # 직원 상세
│   └── employee_form.html     # 직원 등록/수정
├── static/                     # 정적 파일
│   ├── css/
│   │   └── style.css          # 스타일시트
│   ├── js/
│   │   └── main.js            # JavaScript
│   └── images/                # 이미지
├── data/                       # 데이터 저장
│   └── employees.json          # 직원 데이터
└── prototype/                  # 프로토타입 HTML
    └── demo_layout.html       # 디자인 레퍼런스
```

## 설치 및 실행

### 1. 저장소 클론 (또는 프로젝트 디렉토리로 이동)

```bash
cd /home/thekimsangjin/workspace/insacard
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

### 4. 애플리케이션 실행

```bash
python app.py
```

### 5. 브라우저에서 접속

```
http://localhost:5000
```

## 라우팅 구조

| 메서드 | 엔드포인트 | 설명 |
|--------|-----------|------|
| GET | `/` | 대시보드 |
| GET | `/employees` | 직원 목록 |
| GET | `/employees/<id>` | 직원 상세 정보 |
| GET | `/employees/new` | 직원 등록 폼 |
| POST | `/employees` | 직원 등록 처리 |
| GET | `/employees/<id>/edit` | 직원 수정 폼 |
| POST | `/employees/<id>/update` | 직원 수정 처리 |
| POST | `/employees/<id>/delete` | 직원 삭제 |
| GET | `/search?q=검색어` | 직원 검색 |

## 데이터 모델

### Employee (직원)

```python
{
    "id": int,              # 직원 ID (자동 생성)
    "name": str,            # 이름
    "photo": str,           # 사진 URL
    "department": str,      # 부서
    "position": str,        # 직급 (사원, 대리, 과장, 차장, 부장, 이사, 상무, 전무, 대표)
    "status": str,          # 재직 상태 (active, warning, expired)
    "hireDate": str,        # 입사일 (YYYY-MM-DD)
    "phone": str,           # 전화번호
    "email": str            # 이메일
}
```

## 샘플 데이터

시스템에는 25명의 샘플 직원 데이터가 포함되어 있습니다. `data/employees.json` 파일에서 확인할 수 있습니다.

## 개발 환경

- **Python**: 3.8 이상
- **Flask**: 3.0.0
- **Flask-WTF**: 1.2.1
- **WTForms**: 3.1.1

## 디자인 시스템

- **색상 팔레트**: 15단계 따뜻한 그레이 톤
- **타이포그래피**: Inter 폰트 (10단계 크기)
- **간격 시스템**: 13단계 정밀 간격
- **반응형**: Mobile(~767px), Tablet(768-1023px), Desktop(1024px~)

## MVP 제외 기능 (Phase 2 계획)

- 사용자 인증 및 권한 관리
- 파일 업로드 기능
- 데이터베이스 연동 (SQLite/PostgreSQL)
- RESTful API 엔드포인트
- 단위 테스트 및 통합 테스트
- 배포 설정 (Docker, Gunicorn 등)
- 이력 및 경력 상세 정보 관리
- 인사기록 관리 기능
- 엑셀/CSV 내보내기

## 문제 해결

### 포트가 이미 사용 중인 경우

```bash
# app.py의 마지막 줄을 수정
app.run(debug=True, host='0.0.0.0', port=5001)
```

### 데이터 초기화

```bash
# data/employees.json 파일을 삭제하면 빈 상태로 시작됩니다
rm data/employees.json
```

## 라이센스

이 프로젝트는 교육 및 학습 목적으로 제작되었습니다.

## 작성일

2025-11-21

