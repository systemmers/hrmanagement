---
description: 프로토타입 생성 및 개발 명령어
category: development
type: command
version: 1.0.0
author: Claude Code Assistant
created: 2025-06-26
updated: 2025-06-26
tags: [prototype, mvp, prd, development, html, css, javascript]
priority: high
status: active
---

# $arguments 명령어

Claude Code 커스텀 명령어로 $arguments를 분석하여 MVP 또는 PRD 문서를 생성하고 프로토타입을 개발하는 통합 명령어입니다.

## 기본 동작
- HTML, CSS, JavaScript로 구성된 프로토타입 생성
- 코딩순서 HTML > CSS > Javascript
- 기본적으로 HTML 파일 실행 가능한 형태로 출력
- 프로토타입 전용 프로젝트 폴더 구조 자동 생성
- 하드코딩, 인라인코드 금지 (단, --min_limit 옵션 시 예외)
- MCP 도구 전체 활용
- 파일의 코드라인 수는 최대 1000라인을 넘지 않으며, 모듈화 및 분할 개발한다.

## 옵션 카테고리

### 1. 문서 생성 옵션
- `--intention` : 의도를 파악하여 피드백
- `--prd` : Product Requirements Document 생성 (문서만)
- `--mvp` : Minimum Viable Product 문서 생성 (문서만)
- `--roadmap` : 분석 또는 설계한 자료를 근거하여 개발 로드맵 생성 (phase → task → sub_task 구조)
- `--str` : 프로젝트 구조 출력 (백엔드, 프론트엔드, 사이트맵 리스트와 트리구조)
- `--str_code` : 코드 구조 분석 (함수, 클래스, 의존성 리스트)
- `--quick_prd` : 빠른 검증용 간소화된 PRD (핵심 기능만)
- `--quick_roadmap` : 1-2주 단위 간소화된 로드맵 (phase → task → sub_task 구조)
- `--validate` : 검증 중심 문서 (사용자 시나리오, 테스트 케이스)
- `--design` : 레이아웃, uiux, 스타일, 컴포넌트, 인터페이스, db 구조도를 생성하여 md로 저장
- `--seq` : sequential thinking mcp
- `--c7` : context7 mcp
- `--todolist` : todolist에 근거한 진행
- `--checklist` : 체크리스트 작성과 피드백 
- `--list` : 리스트화
- `--architecture`: 프로젝트구조, 디렉토리, 파일구조 출력

### option
- `tree` : 트리구조
- `list` : 리스트 

### 2. 개발 실행 옵션
- `--build` : 생성된 문서 또는 arguments 기반으로 실제 개발 시작 (개발 트리거)
- `--function` : 기능 중심 개발

### 3. 구조 및 모듈 옵션
- `--module` : 모듈 단위로 분할 개발
- `--multi` : 다중 페이지 애플리케이션

### 4. 환경 및 최적화 옵션
- `--flask` : Flask 환경으로 실행 (백엔드 포함)
- `--min` : 파일 최소화 (각 코드별 1개씩)
- `--min_limit` : 단일 파일 인라인 구현 (HTML/CSS/JS 통합)
- `--min_limit_py` : 단일 Python 파일로 Flask 앱 통합

### 5. 기술 스택 옵션
- `--bootstrap` : Bootstrap 5 기반 UI 프레임워크
- `--tailwind` : Tailwind CSS 기반 스타일링
- `--vanilla` : 순수 HTML/CSS/JS (프레임워크 없음)
- `--wireframe` : 와이어프레임 구조

### 6. 데이터 및 상태 관리 옵션
- `--mockdata` : 목업 데이터 자동 생성
- `--api` : REST API 목업 서버 포함

### 7. 문서화 옵션
- `--docs` : 기술 문서 자동 생성

### 8. 페르소나 옵션
- `--persona-user` : 사용자 관점 페르소나 적용 (UX/UI 중심 설계)
- `--persona-dev` : 개발자 관점 페르소나 적용 (기술적 구현 중심)
- `--persona-pm` : 프로젝트 매니저 관점 페르소나 적용 (관리/일정 중심)
- `--persona-designer` : 디자이너 관점 페르소나 적용 (시각적 설계 중심)
- `--persona-client` : 클라이언트 관점 페르소나 적용 (비즈니스 요구사항 중심)
- `--persona-qa` : QA 테스터 관점 페르소나 적용 (품질 검증 중심)
- `--persona-stakeholder` : 이해관계자 관점 페르소나 적용 (전략적 관점)
- `--persona-analyst` : 분석가 관점 페르소나 적용 (데이터 분석 중심)
- `--persona-security` : 보안 전문가 관점 페르소나 적용 (보안 중심 설계)
- `--persona-architect` : 시스템 아키텍트 관점 페르소나 적용 (구조 설계 중심)



---

## 실행 환경

### 기본 환경
- 정적 HTML/CSS/JS 프로토타입
- 자동으로 프로토타입 전용 디렉토리 생성

### Flask 환경
- `--flask` 옵션 시 백엔드 연동 프로토타입
- Python Flask 서버 포함

## 사용 예시

### 기본 프로토타입 생성
```
@prototype 웹사이트 제작
```

### 빠른 검증 중심 개발
```
@prototype --quick_prd --validate --build 웹사이트 제작
```

### 간소화된 로드맵으로 개발
```
@prototype --quick_roadmap --build 웹사이트 제작
```

### 문서 생성 후 개발
```
@prototype --prd --roadmap --build 웹사이트 제작
```

### 코드 구조 분석 포함
```
@prototype --str_code --build 웹사이트 제작
```

### Flask 백엔드 포함 개발
```
@prototype --flask --api --build 웹사이트 제작
```

### Tailwind CSS 기반 개발
```
@prototype --tailwind --build --multi 웹사이트 제작
```

### 단일 파일 인라인 구현
```
@prototype --min_limit --vanilla 웹사이트 제작
```

### Flask 단일 파일 구현
```
@prototype --min_limit_py --flask 웹사이트 제작
```

## 프로토타입 중심 접근법

### 빠른 검증 워크플로우
프로토타입은 **빠른 검증**이 목적이므로 다음 순서로 진행:

1. **핵심 기능 정의** (`--quick_prd`)
2. **검증 시나리오 작성** (`--validate`)
3. **간소화된 로드맵** (`--quick_roadmap`)
4. **빠른 개발** (`--build`)

### 프로토타입 문서 특징
- **PRD**: 핵심 기능 3-5개만 정의
- **로드맵**: 1-2주 단위, 최대 4주
- **검증**: 실제 사용자 시나리오 중심
- **기술적 세부사항**: 최소화

### 빠른 개발 원칙
1. **기능 우선**: 디자인보다 기능 검증
2. **최소 구현**: 핵심 기능만 구현
3. **빠른 반복**: 1-2일 단위로 수정
4. **사용자 피드백**: 실제 사용자 테스트 중심

---


## 옵션 조합 가이드

### 빠른 검증 워크플로우 (권장)
```
@prototype --quick_prd --validate --quick_roadmap --build [프로젝트명]
```

### 문서 중심 워크플로우
```
@prototype --prd --mvp --roadmap --str [프로젝트명]
```

### 개발 중심 워크플로우
```
@prototype --build --function --module [프로젝트명]
```

### 풀스택 개발 워크플로우
```
@prototype --flask --api --docs --build [프로젝트명]
```

### UI/UX 중심 개발
```
@prototype --tailwind --build [프로젝트명]
```

### 코드 분석 중심
```
@prototype --str_code --build [프로젝트명]
```

## 주의사항

1. **하드코딩 금지**: 모든 데이터는 동적으로 생성되거나 외부 소스에서 가져와야 함 (단, --min_limit 옵션 시 예외)
2. **인라인코드 금지**: CSS와 JavaScript는 별도 파일로 분리 (단, --min_limit 옵션 시 예외)
3. **MCP 도구 활용**: 모든 작업에서 MCP 도구를 적극 활용
4. **모듈화**: 재사용 가능한 컴포넌트 중심 설계 (단, --min_limit 옵션 시 예외)
5. **문서화**: 코드와 함께 문서 자동 생성

## 출력 구조

### 기본 출력
```
prototype/
├── index.html
├── css/
│   └── style.css
├── js/
│   └── script.js
├── assets/
│   └── images/
└── docs/
    ├── prd.md
    ├── mvp.md
    └── roadmap.md
```

### Flask 환경 출력
```
prototype/
├── app.py
├── templates/
│   └── index.html
├── static/
│   ├── css/
│   ├── js/
│   └── assets/
├── docs/
└── requirements.txt
```

### --min_limit 출력
```
prototype/
└── index.html (모든 CSS, JS가 인라인으로 포함)
```

### --min_limit_py 출력
```
prototype/
└── app.py (Flask 앱과 모든 템플릿이 단일 파일로 통합)
```





