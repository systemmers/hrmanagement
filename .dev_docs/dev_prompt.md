
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


FK 조건
---



-- 경력정보 / 급여를 > 연봉으로 변경, 급여 추가(급여인사람도 있기때문)
-- 추가 필드가 필요한 섹션 및 필드
-- 사이즈 확정 명함, 증명사진



첨부파일 관리
-- 첨부 파일 등록시 필수 서류를 지정하고 회사에서 지정 및 프리셋
-- 그리고 일반적으로 중요 순서대로 나열되게, 첨부서류 현황 및 사이드바 첨부서류에서 확인
-- 저장 규칙
-- 이후 가적으로 법인에서는 회사에서 발생하는 자료, 근테기록 엑셀 파일등 분류별로 저장하기 위한규칙
-- 증명사진은 기본 5개 올려서 제출시 선택하는 기능을 제공, 수량은 변경될수 잇음 > 저장 규칙 변경경




- 사용자 인터페이스 개선


- 은행 공통코드
위에서 언급한 것은 은행은 상세나, 수정에서 기본정보에서 입력하는것으로 이동하는 것이고, 은행의 경우 공통 은행 코드가 세팅 되어 있지만 법인에서 은행코드를 추가적으로 추가할 수 있거나 삭제할 수 있게 하여라.  





변수를 사용하는 것과 상수화를 하는것의 차이점은 무엇인가
모듈화
믹스인





직원 게정은 순서를 계정 생성 > 계정로드 정보입력
직원 계정으로 전환 후 정보입력
- 초기 비번을 알고 있기 떄문에 전환이 가능
- 직원이 최초로그인 하거나, 비번을 변경할시 전환불가능



---




읜존성 및 구조화
복잡하게 중복, 중첩 코딩
스파게티코드, 레거시 코드드


구조화 
미사용 코드 및 클래스
일관된 주석처리
미사용 파일 
중앙화와 일반화 구조

Inline 금지
soc
modular
convention 준수수
네이밍 스페이스, 네이밍

코드 재정의


re-check


스캔



js, py 기능 역할할 분리가 명확한지 검토하여라.

js, py 백엔드 프론트엔드








-----


구현 기능, 기존기능, 활용기능
초기 비밀번호는 세팅 고정세팅 일반세팅

명함 자동 생성기능

시나리오

개인정보


3. list.html > corporate 
- 도메인으로 이동 처리.
- employee 폴더 삭제



 "패턴 및 중앙화 및 일반화, solid, ssot외 기타 개발 원칙을 체크, 준수하여 계획했는지 검토하여라."


인사카드 필터조건


테이블 헤드 스타일 
읜존관게 분석 제거거

/sc:workflow "개발규칙 및 일관성을 유지 체크를하고 진행" --task --checklist --todolist --test-check --safe



--intention-feedback


--dependency

