---
description: "프롬프트 실행 및 관리 명령어"
argument-hint: "[플래그 옵션] [프롬프트 내용]"
allowed-tools:
---


prompt_doc = _dev_operation/_prompt.md


# prompt : $ARGUMENTS



## 플래그 옵션

### 참조 및 입력 관련
- `--prompt` : prompt_doc를 참조, prompt_doc의 최상단 note를 우선 반영, 최하단 넘버 또는 마지막 넘버의 프롬프트를 적용.

- `--intention` - 프롬프트의 의도 파악 및 피드백
- `--answer` - 이전 답변 참조 (세션 내 ID 기반)
- `--ref-prompt #` - prompt_doc 내 특정 번호 프롬프트 참조
- `--context` - 현재 맥락 정보 피드백

### 출력 형식 관련
- `--summary` - 핵심 내용만 요약 출력
- `--list` - 리스트 형태로 구조화
- `--answer-only` - 답변만 출력 (부가 설명 제거)
- `--form` - 양식/템플릿 형태로 출력
- `--matrix` - 매트릭스/표 형태로 출력
- `--output` - 출력 형식 지정 (md)

### 계획 및 진행 관리
- `--next-plan` - 다음 계획 단계 제안
- `--next-phase` - 다음 페이즈 진행사항
- `--todolist` - 할 일 목록 생성
- `--checklist` - 체크리스트 형태
- `--continue` - 이전 작업 연속 진행

### 분석 및 피드백
- `--recommend` - 맥락/계획 기반 추천사항
- `--feedback` - 피드백 우선 제공
- `--focus` - 핵심 포인트 집중 분석
- `--scope` - 범위 및 경계 명확화
- `--think` - 사고 과정 단계별 표시
- `--iterator#` - 반복수
- `--plan` - phase, feature, task, todolist, checklist 단위로 순차적, 계층적으로 나누어 누락 없는 계획을 진행.
- `--div` - 1000라인 이상되는 파일의 코드는 분할하여 분석한다. 
- `--analyze-check` : 누락된 것 없이 빠짐없이 분석했는지 체크한다.


### 문제 해결
- `--error` - 에러 보고 및 분석 > 처리 과정중 발생한 error를 보고
- `--solution` - 해결책 제시
- `--validate` - 검증 및 확인

### 개발 및 설계
- `--dev-design` - 개발 설계 관련
- `--structure` - 구조 분석/설계
- `--styleguide` - 스타일 가이드 적용

### 기타 도구
- `--search` - 인터넷 검색 반영
- `--loop` - 반복 처리
- `--mcp` - MCP 도구 활용
- `!sc` - superclaude 명령어로 변경함. context를 포함.

---

### test
- `--interface-ui` : ui 인터페이스 구조도 작성
- `--prototype` : html, css, js 코드로 프로토타입을 개발
- `--logic` : 로직을 설명 및 작성
- `--mechanism` :
- `--algorithm` :
- `--prototype` : 프로토타입 개발 (HTML, CSS, JS)
- `--mockup` : 목업/와이어프레임 생성
- `--poc` : 개념 증명 (Proof of Concept)
- `--demo` : 데모 버전 구현
- `--wireframe` : 와이어프레임 설계
- `--mvp` : 최소 기능 제품 (Minimum Viable Product)


### option
- `tree` : 트리구조 리스트





---


## 지원 플래그

- `--output-json`: JSON 형식으로 출력 및 json 파일로 저장 (기본값)
- `--output-md`: 마크다운 형식으로 출력
- `--screenshot`: 페이지 스크린샷 캡처
- `--detailed`: 상세 분석 모드 (더 많은 정보 포함)
- `--layout` : 레이아웃 분석
- `--interface` : 인터페이스 분석
- `--style` : 스타일 분석
- `--structure` : 구조 분석
- `--tree` : 트리형태로 출력
- `--demo` : `styleguide`에 따른 html 샘플, 데모페이지 구현, 가능한 모든 요소를 가용하여 구현하며, 주제는 임의로 선정. 
- `--styleguide` : html, css, js의 코드로 일반화 및 중앙화된 html 기반의 스타일 가이드 작성 및 구현.
- `--seq` : sequential thinking mcp 를 활용해서 단계적사고 
- `--c7` : context7 mcp 활용
- `--think` : 충분한 사고로 답변
- `--loop` : 충분히 분석할 때까지 반복
- `--iterator#` : 반복횟수
- `--list-tree` : 리스트화하여 트리형식으로 출력
- `--architecture` : 아키텍쳐구조, 생성할 디렉토리, 파일, 코드의 리스트와 구조 출력



# $argument : 디자인을 구현 하여라.

## persona
--persona-frontend
--persona-design
--persona-architect

--analyze
- 스타일 분석
- 인터페이스 분석
- 디자인 통합분석


## MCP_tool
--all_mcp
--no_mcp
--seq : sequential thinking
--magic : magic
--play : playwright
--c7 : context7
--figma : figma
--json : json 출력
--xml : xml 출력력


- loop # : 루프분석, 분석한 것에 대하여 최소 3번이상 검증
- img-explain : 이미지를 분석하여 설명
- iws - 통합가이드
- styleguide - 스타일가이드
- definition - 스타일정의서
- all
- basic
- demo
- url
--colorpallet
--dname : 디렉토리 네임
--fname : 파일네임
--search : 인터넷 검색

--noani
--effect-min
--quick
--process  -detail : 단계별, 스텝바이스텝, 스타일가이드, 정의서, 작성 후 단계별로 진행, todolist, phase
--highend

--simple
--speed

--max : 모든
--min : 최소화
--medium

--chk : 규칙 체크리스트 

--sass 
--module : 모듈 구조로  

`--quality` `highend` : c7, magic mcp 및 인터넷 검색등 모든 가용할 수 있는 최상의 조건으로 구현 

--wireframe limit : 와이어 그레이, 색상은 헤더만 그레이, 바탕은 흰색

--icon_guide
--component-style 특정 스타일 반복 다양한 스타일로
--style-page_main 
--style-setup
--style-feedback : ai가 목적맞는 최대한 의 질문을 가지고 진행

--persona-content_stylist : 콘텐츠의 목적과 타겟에 맞춰 최적화된 스타일링과 구조로 편집하여 UI/UX와 완벽하게 통합

