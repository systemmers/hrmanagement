# dev_set

git : https://github.com/systemmers/insacard.git



- 스타일 가이드 정의
- 프로젝트 구조정의 : 개념, 물리적
- 환경설정
- 로그인 > 서비스 선택화면 > 서비스 메인화면
- db스키마 설계
- jinja2
- 스타일가이드 
- 데모 이미지 데이터 25명 : /members/A
- 화면설계
- phase 1 : sever active "로그인 에서 메인페이지", db init 과 세팅

- live_dev
- --debug-mode

- process : workflow <> doc_checklist : 워크플로우 문서에서 계획하에 작업을 진행하며, 작업단계마다 문서와 비교하며 체크리스트에 피드백

- 기본정보
- 인사기록정보

---

기본 레이아웃
- 헤드 : 고정
- 레프트 사이드
- 메인
- 라이트 사이드

---
workflow
process

--- 
# Load map


1차
## milestone


2차


3차


4차


5차

---


목적 
- 직원 인사정보 취합 및 인사카드 관리
- 인사정보 관리
- 인사정보 관련 파일관리
- 인사정보 변동 기록 및 관리 : 관리자만 열람가능
- 인사평가 관리
- 직원파일정보 카드 : 자동출력
- 계약정보 : 자동출력 
- 간편하고 효율적이며, 핵심적 관리
- 근로기준법 서류 충족
- 충족정보, 서류 및 체크, 점검
- 경력관리
- 



1. 개발환경
- 파이썬 플라스크
- mvp, startup 구조
- 기반파일 : insacard_structure.md


2. 개념구조
- 직원 인사 기본정보
- 직원 인사 기록
- 직원 인사 파일관리
- 인사평가
- 직원 계정으로 개별정보 입력
- 관리자 직원정보 취합 및 CRUD



3. 화면구조 > 스크롤 시 고정


4. 출력
- 본사 스타일 인사카드 : pdf, print
- 근로자명부 엑셀 파일

5. flow
- 로그인 > 인사기록카드 메인
- 로그인 > 사용자 로그인 > 정보확인 및 등록, 수정정
- 로그인 > 관리자 로그인 > 대시보드 메인 > 레프트 사이드바(직원등록, 조회) > 직원 조회방식(조직도 내 이름 클릭, 이름검색, 사진선택) > 메인 렌더링
    - 직원 등록 및 인사카드 작성
    - 조회시 해당 사이드바에 조직도 및 직원 사진, 이름 조회 1Xn 

- 오른쪽 사이드바 : 직원 선택시 맵핑된 등록한 인사정보관련 파일 보여줌줌 = 주민등록등본, 이력서, 기타서류파일일

6. 사이트맵
- 인사카드
- setting : 조직, 직급, 직책, 이메일 도메인, 회사정보, 회사로고

- 인사정보 입력 폼 수정, 저장
- 인사카드 보기 > 프린터 
- 인사기록 입력력


# AI
- 첨부파일 업로드시 첨부파일을 분석하고 내용을 요약한다.


- 근로감독관 제출 서류 목록
    - 근로자명부
    - 임금대장
    - 근로계약서
    - 4대보험 가입자명부 (국민연금, 건강보험, 고용보험, 산재보험)

    - 취업규칙 : 법령을 검토하여 수정제안

    - 출퇴근 기록부 (근태관리대장)
    - 연차휴가대장
    - 임신·출산·육아휴직 관련 서류
    - 재해발생보고서
    - 산업안전보건 관련 기록(교육일지, 점검표 등)
    - 직장 내 괴롭힘·성희롱 예방교육 자료
    - 기타 법령상 요구되는 노동관계 서류

    - 입퇴사 정보


근로감독관 제출서류 자동 생성을 위해 인사기록카드를 확장·관리하는 포털 사이트
- 시드 정보: 인사기록카드 정보



### setting
- 조직도
- 직급
- 직책
- 호봉
- 전화번호
- 이메일
- 계정등록
- 회사정보
- 평가등급
- 급여 내역

### 관리자
- 평가항목 세팅



# 인사기록카드에 포함될 정보 리스트

디자인
- 스타일 card : 회사기준 디자인
- 일반 문서형식
- 테이블 형식



---


- 인사카드 디자인 
- 로고
- 세팅 필수 체크

- 소속정보
    - 회사
    - 소속

- 기본정보
    - 사원번호 : 자동 부여, 사용한 번호는 사용금지
    - 사진
    - 성명(한글/영문)
    - 영어이름
    - 주민등록번호/외국인등록번호
    - 생년월일 : 주민등록번호로 자동 인식, 수정가능
    - 성별 : 주민등록번호로 자동 인식
    - 연락처(휴대폰/비상연락처)
    - 비상연락처(연락처, 구분)
    - 이메일(회사, 본인)
    - 주소(주민등록상/실거주지)

    - 병역정보
    - 보훈


- 소속정보
    - 소속부서(부서/팀) : 세팅 연결, 최종부서
    - 직급/직책 : 세팅 연결
    - 입사일자/퇴사일자
    - 고용형태(정규직, 계약직, 무기/기간, 인턴 등)
    - 근무지


- 계약정보 : 현재 계약정보
    - 근로계약 유형
    - 계약기간(시작일/종료일)
    - 직무 및 담당업무
    - 급여형태 및 금액
    - 근로시간(시업/종업/주간근로시간)
    - 휴게시간
    - 계약 갱신 여부
    - 계약서 파일 첨부


- 인사정보 : 테이블 형식

- 근로계약정보 : 테이블 형식, 기록, 각 리스트 클릭으로 세부정보 확인
    - 테이블 정보:
        - 근로계약 유형
        - 체결일
        - 계약기간(시작/종료)
        - 고용형태(정규직/계약직/인턴 등)
        - 계약상태
    
    - 클릭시 세부정보:
        - 직무 및 담당업무
        - 근로시간(시업/종업/주간근로시간)
        - 휴게시간
        - 시용기간, 수습기간 (1년 미만내 적용)
        - 수습평가
        - 평가서 연동
        - 근로계약서 스캔본 연동

- 연봉계약정보 : 테이블 형식, 기록, 각 리스트 클릭으로 세부정보 확인
    - 테이블 정보:
        - 계약년도
        - 체결일
        - 계약기간(시작/종료)
        - 급여형태(월급/시급/연봉)
        - 계약상태
    
    - 클릭시 세부정보:
        - 급여 세부내역 및 구조
        - 지급계좌
        - 연봉계약서 스캔본 연동


        
    - 호봉/승급/승진 이력
        - 테이블: employee_promotions
        - 필드:
            - id (PK)
            - employee_id (FK)
            - promotion_type (승진/승급/호봉)
            - previous_position (이전 직급/호봉)
            - new_position (변경 직급/호봉)
            - effective_date (발령일자)
            - reason (사유)
            - evaluation_id (FK, 평가서 연동)
            - created_at
            - updated_at
    
    - 부서이동/발령 이력
        - 테이블: employee_transfers
        - 필드:
            - id (PK)
            - employee_id (FK)
            - transfer_type (부서이동/발령/파견)
            - previous_department (이전 부서)
            - new_department (변경 부서)
            - previous_position (이전 직책)
            - new_position (변경 직책)
            - previous_workplace (이전 근무지)
            - new_workplace (변경 근무지)
            - effective_date (발령일자)
            - reason (사유)
            - created_at
            - updated_at
    
    - 평가/발령일자
        - 테이블: employee_evaluations
        - 필드:
            - id (PK)
            - employee_id (FK)
            - evaluation_period (평가기간: 3개월/6개월/1년)
            - evaluation_date (평가일자)
            - evaluation_score (평가점수)
            - evaluation_grade (평가등급: S/A/B/C/D)
            - action_taken (후속조치: 승진/승급/유지/경고 등)
            - created_at
            - updated_at
    
    - 급여이력/변동내역, 연봉계약서 연동
        - 테이블: employee_salary_history
        - 필드:
            - id (PK)
            - employee_id (FK)
            - effective_date (적용일자)
            - salary_type (급여형태: 월급/시급/연봉)
            - previous_amount (이전 급여액)
            - new_amount (변경 급여액)
            - change_reason (변경사유: 승진/승급/계약갱신/기타)
            - change_percentage (변동률 %)
            - related_promotion_id (FK, 승진이력 연동)
            - related_evaluation_id (FK, 평가이력 연동)
            - notes (비고)
            - created_at
            - updated_at


- 프로젝트 : 
- 상벌
- 근태



---



---

- 학력 및 경력
    - 최종학력
        - 학교명
        - 전공
        - 졸업구분(졸업/수료/중퇴/재학)
        - 입학일자/졸업일자
        - 학위(학사/석사/박사)
        - 성적(평점/백분율)

    - 경력사항 : 전직장 인사담당자 입력
        - 테이블: employee_careers
        - 필드:
            - id (PK)
            - employee_id (FK)
            - company_name (회사명)
            - position (직책/직위)
            - department (부서)
            - start_date (입사일)
            - end_date (퇴사일)
            - job_description (담당업무)
            - employment_type (고용형태)
            - salary_info (급여정보, 선택)
            - reason_for_leaving (퇴사사유)
            - created_at
            - updated_at
    
    - 프로젝트 참여이력
        - 테이블: employee_projects
        - 필드:
            - id (PK)
            - employee_id (FK)
            - project_name (프로젝트명)
            - client_name (고객사/발주처)
            - project_role (역할/직책)
            - start_date (시작일)
            - end_date (종료일)
            - project_description (프로젝트 설명)
            - technologies_used (사용기술/스킬)
            - team_size (팀 규모)
            - achievements (주요 성과)
            - project_status (상태: 진행중/완료/중단)
            - created_at
            - updated_at
    
    - 상벌이력
        - 테이블: employee_rewards_penalties
        - 필드:
            - id (PK)
            - employee_id (FK)
            - type (구분: 포상/징계)
            - category (세부구분: 표창/상금/경고/감봉/정직/해고 등)
            - reason (사유)
            - decision_date (결정일자)
            - effective_date (시행일자)
            - amount (금액, 해당시)
            - penalty_period (징계기간, 해당시)
            - decision_authority (결정권자)
            - related_document_path (관련문서 경로)
            - notes (비고)
            - created_at
            - updated_at
    

    - 자격증/면허증
        - 테이블: employee_certifications
        - 필드:
            - id (PK)
            - employee_id (FK)
            - certification_name (자격증명)
            - issuing_organization (발급기관)
            - certification_number (자격증번호)
            - issue_date (취득일자)
            - expiry_date (만료일자, 선택)
            - grade_level (등급/급수, 선택)
            - attachment_path (첨부파일 경로)
            - created_at
            - updated_at
    
    - 어학능력
        - 테이블: employee_languages
        - 필드:
            - id (PK)
            - employee_id (FK)
            - language_name (언어명)
            - proficiency_level (숙련도: 초급/중급/고급/원어민)
            - test_name (시험명: TOEIC, TOEFL, JLPT 등)
            - test_score (점수)
            - test_date (시험일자)
            - certificate_number (증명서번호)
            - expiry_date (유효기간)
            - attachment_path (첨부파일 경로)
            - created_at
            - updated_at
    
    - 교육이수
        - 테이블: employee_trainings
        - 필드:
            - id (PK)
            - employee_id (FK)
            - training_name (교육명)
            - training_type (교육구분: 직무교육/법정교육/외부교육/사내교육 등)
            - training_organization (교육기관)
            - training_period_start (교육시작일)
            - training_period_end (교육종료일)
            - training_hours (교육시간)
            - training_location (교육장소)
            - training_cost (교육비용)
            - completion_status (이수상태: 이수/미이수/진행중)
            - certificate_issued (수료증발급여부)
            - certificate_number (수료증번호)
            - training_score (교육점수/평가)
            - attachment_path (첨부파일 경로)
            - notes (비고)
            - created_at
            - updated_at


- 4대보험 정보
    - 국민연금/건강보험/고용보험/산재보험 취득 및 상실일자
    - 보험번호



- 법정의무사항 및 특이사항
    - 테이블: employee_legal_matters
    - 필드:
        - id (PK)
        - employee_id (FK)
        - employment_rules_agreement (취업규칙 동의여부)
        - employment_rules_date (취업규칙 동의일자)
        - privacy_agreement (개인정보 동의여부)
        - privacy_agreement_date (개인정보 동의일자)
        - military_service_status (병역상태: 군필/면제/미필/해당없음)
        - military_branch (군별: 육군/해군/공군/해병대)
        - military_rank (계급)
        - military_service_period (복무기간)
        - discharge_date (전역일자)
        - disability_status (장애여부)
        - disability_grade (장애등급)
        - disability_type (장애유형)
        - veterans_status (보훈대상여부)
        - veterans_type (보훈유형)
        - special_notes (기타 특이사항)
        - created_at
        - updated_at

        


- 서류/첨부파일 : 순서
    - 이력서
    - 자기소개서
    - 주민등록등본
    - 가족관계증명서
    - 자격/면허증 사본
    - 경력증명서
    - 건강보험자격득실확인서
    - 국민연금가입자가입증명서
    - 근로소득원천징수영수증
    - 기타 각종 인사관련 파일

(※ 실제 회사 상황이나 관련 법령에 따라 추가/수정 가능)



---



- 자동 생성 가능한 서류:
    - 근로자명부
    - 임금대장 (기초정보 및 급여 데이터 연동 시)
    - 근로계약서 (기본계약정보 입력 시)
    - 4대보험 가입자명부 (사내 가입정보 입력 시)
    - 출퇴근 기록부(근태관리대장, 출퇴근/휴가 정보 입력 시)
    - 연차휴가대장 (휴가정보 연동 시)
    - 입퇴사 정보 보고서
    - 인사카드(출력용, PDF/Excel)
    - 재직증명서 등 인사 관련 각종 증빙
    - 회사명함


- 자동 생성이 어려운/불가능한 서류:
    - 취업규칙 (법령 및 회사내규 별도 검토, 수동작성 필요)
    - 산업안전보건 관련 기록(교육일지, 점검표 등 활동별 실시간 데이터 필요)
    - 직장 내 괴롭힘·성희롱 예방교육 자료 (별도 교육이력, 수동 등록 필요)
    - 임신·출산·육아휴직 관련 서류 (개별 상황별 근거자료 수집 필요)
    - 재해발생보고서 (사건 발생 시 별도 입력 필요)
    - 법령상 기타 요구 문서(외부 감독자료 등 수작업 필요)


- service contents 
    - 법령정보





인사카드 
3개달 단위로 인사평가 카드



수습 기간
1주, 2주, 1개월
수습기간 연장



- 노사위원회 




화면설계

회사정보 세팅


로그인 : 사용자, 관리자

사용자
1. 네비게이션
- 메인 : 대시보드
- 인사카드 : 조회, 입력, 수정, 업데이트
- 기본정보
- 인사기록 정보
- 인사파일 관리

2. 네비게이션
- 메인 : 대시보드
- 직원조회 : 카드형 리스트
- 조직조회 : 조직 클릭시 멤버 조회
- 직원 상세 : 직원정보, 직원 인사기록정보

관리자










---
웹으로 정보를 취한다.

포트폴리오, 추천서

인사정보 공유 승인/거부, 실시간 업데이트 - 법인 접근 - 인사정보 활용가능

---




1. 

- 기본 입력, db관리체계 구현
- 인사정보 입력 > 인사정보 저장, 수정 > 인사정보 로드 > 인사카드 출력

2. 

db 정보를 활용한 추가 플랫폼
- 증명서 및 근로계약서등 문서 작성
- 평가서, 네트워크 평가서 작성

3. ai 
- 첨부한 문서를 ai가 분석하여 자동입력
- 첨부한 영수증을 ai가 분석하여 자동입력

