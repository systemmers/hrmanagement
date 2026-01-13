
---

# git master id
- --commit --branch-new "hrm-projekt-yymmddnn" --push
- hrm-projket-20
- hrm-projket-21

---


/sc:explain "오류의 근본원인이 무엇인가?" --simple --beginer --metaphor
/sc:workflow --patterns-dev --task --checklist --todolist --test-check --preview 
/sc:workflow --task --checklist --todolist --test-check --safe --check "dependency, rules, test, lagacy, pattern"
---

# rules, check
# Matrix
## 개발 원칙 (Development Principles)

### 코드 품질 원칙
- 중앙화(Centralization) - 공통 로직을 한 곳에서 관리
- 일반화(Generalization) - 재사용 가능한 범용 코드 작성
- 코드 중복, 중첩 금지 - DRY(Don't Repeat Yourself) 원칙
- 코드 재활용 - 기존 컴포넌트 최대한 활용
- 하드코딩, 인라인 코딩 금지 - 설정 파일 및 상수 활용
- 코드 재정의 금지 - 기존 정의된 코드 재사용

### 네이밍 및 구조 원칙
- 네이밍, 네이밍 스페이스 준수 - 명확하고 일관된 이름 사용
- 컨벤션 준수 - 프로젝트 코딩 스타일 가이드 준수
- 모듈화 - 기능별 독립적인 모듈 구성
- 규칙적 구조화 유지 - 일관된 디렉토리 및 파일 구조
- 스타일 일관성 준수 - 코드 포맷팅 통일

### 설계 원칙
- SOC(Separation of Concerns) 준수 - 관심사의 분리
- SOLID 원칙 - 객체지향 설계 5대 원칙
- SSOT(Single Source of Truth) 원칙 - 단일 진실 공급원
- 패턴(Pattern) - 검증된 디자인 패턴 활용
- 일관된 아키텍처 구조 유지 - 전체 시스템 구조 일관성

### 작업 범위 원칙
- 지시한 것만 진행 - 요구사항 범위 준수
- 목적 외에 다른 코드에 영향을 주지 말것 - 사이드 이펙트 최소화
- 최대한 분할 작업 - 작은 단위로 작업 분리

### 추가 개발 가이드
- 상수화 - 매직 넘버/문자열 상수로 정의
- 표준화 - 표준 규격 및 프로토콜 준수
- 통일성 - 전체 시스템의 일관성 유지
- API 설계 - RESTful 원칙 준수
- Mixin 활용 - 공통 기능 믹스인으로 분리
- 검증 우선 - 필요성과 근거에 의한 구현
- 복잡도 최소화 - 단순하고 명확한 코드 작성

## 개발 워크플로우 (Development Workflow)

### 작업 프로세스
1. **Git 관리** - 브랜치 전략 및 커밋 규칙 준수
2. **Plan** - 작업 계획 수립
3. **Verify** - 규칙 및 체크리스트 검증
4. **Workflow** - 작업 흐름 정의
5. **Implement** - 구현
6. **Test** - 단위/통합 테스트
7. **Debug** - 디버깅 및 수정
8. **Review** - 코드 리뷰

### 필수 작업 항목
- 레거시 파일 및 코드 정리
- DB 마이그레이션 관리
- 스크린샷 및 테스트 결과 비교
- 설계 패턴 파악 및 문서화
- `--preview` 미리보기 확인
- `--update` 업데이트 적용


Integration: 기존 시스템에 새로운 디자인을 통합 ✅ (가장 적합)
Adapter: 서로 다른 인터페이스를 연결하는 패턴 (이 경우는 해당 없음)
Migration: 기존 코드를 새 시스템으로 이전
Implementation: 디자인을 코드로 구현
Adoption: 새로운 디자인 시스템을 채택
Modify/Edit
Improve/Refactor
Debug


# today working



--- 
# dashboard, matrix



---
# action, demand, prompt



/sc:workflow "개발규칙 및 일관성을 유지 체크를하고 진행" --task --checklist --todolist --test-check --safe



--intention-feedback

--dependency

/sc:improve @.dev_docs/dev_plans/style_refac.md --seq --think-hard --intention-feedback --verification @agent-frontend-architect @agent-refactoring-expert --dependency 

--priority-level

---

uxui


hooks : 
context fork
lsp


http://localhost:5200/styleguide/components/attachment
