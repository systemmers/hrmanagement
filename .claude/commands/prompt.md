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


