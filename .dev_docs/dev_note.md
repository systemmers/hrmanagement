
# demand / condition /comunication



## note



# api_key_gcloude




# plan

@ 복잡하면 안된다. 



---



## 통합 사이드바 구조


### 개인 (직원) 사이드바
대시보드
 내 현황

내 정보
 프로필
 인사카드

계약 관리
 내 계약
 계약 요청

계정 관리
 계정 설정
 공개 설정


### 법인 (관리자) 사이드바
대시보드
 직원 현황

직원 관리
 직원 목록
 계정 생성


계약 관리
 계약 목록
 계약 요청
 대기 중

법인 관리
 법인 정보
 조직 관리
 사용자 관리
 분류 옵션 관리 > 삭제 이동 법인설정정

계정 관리
 관리자 프로필
 법인 설정 > 고용정책 탭을 분류옵션으로 변경  




데이터가 복잡합니다. admin_global의 실제 company_id를 확인하겠습니다.


3. list.html > corporate 
- 도메인으로 이동 처리.
- employee 폴더 삭제


스탭샷을 처리하는 것이이


근본적 원인을 제거, 임시조치가 아니라 

로직검증


 경력정보와 자격증 템플릿을 수정하고, 어학 템플릿은 매크로를 사용하고 있어 다른 방식으로 처리합니다.


 " "패턴 및 중앙화 및 일반화, solid, ssot외 개발 원칙을 체크, 준수하고 안전하게 개발한다."


---

## User-Employee 조회 규칙 (하이브리드 접근법)

> 2025-12-25: BUG-1 수정 및 조회 로직 명확화

### 계정 타입별 조회 경로

#### employee_sub 계정 (법인 직원)
1. `User.employee_id` 있으면 → 직접 Employee 조회
2. `PersonCorporateContract.employee_number` → 매칭 조회
3. Fallback: `User.email == Employee.email`

#### personal 계정 (개인)
1. PersonCorporateContract만 사용
2. approved 상태만 유효한 연결

### 상태 매핑

| PCC.status | User.is_active | 결과 |
|------------|----------------|------|
| approved | True | 정상 직원 |
| requested | - | 승인 대기 |
| rejected | - | 거절됨 |
| terminated | - | 종료 |
| (없음) + employee_sub | - | 계약 미생성 |

### 페이지별 데이터 소스

| 페이지 | 데이터 소스 | 필터 조건 |
|--------|------------|-----------|
| 직원목록 | Employee + PCC | PCC.status = 'approved' |
| 계정관리 | User (employee_sub) | + PCC.status 표시 (BUG-1 수정) |
| 계약목록 | PersonCorporateContract | company_id / person_user_id |
| 대기목록 | User (employee_sub) | PCC.status != 'approved' |

### N+1 방지 벌크 조회 메서드

```python
# user_employee_link_service.py
get_users_with_contract_status_bulk(user_ids, company_id)
get_employees_with_approved_contracts_bulk(employee_numbers, company_id)

# person_contract_repository.py
get_contracts_by_user_ids_bulk(user_ids, company_id)
get_approved_by_employee_numbers_bulk(employee_numbers, company_id)
get_by_employee_ids_bulk(employee_ids)
```

### SSOT 원칙

- **PersonCorporateContract**: 계약 관계의 유일한 진실의 원천
- **User.employee_id**: employee_sub 계정의 Employee 연결 (하이브리드 호환)
- 두 경로가 병존하되, 계약 상태는 PCC가 권위


----



 "패턴 및 중앙화 및 일반화, solid, ssot외 기타 개발 원칙을 체크, 준수하여 계획했는지 검토하여라."'employee_id'

   - approved 상태만 표시 (21번 원칙 준수)


   ● 문제 발견:
  - Employee 이메일: @company.com
  - User 이메일: @testcorp.co.kr
  - seed 데이터 불일치로 직접 매칭 불가

  직원목록 로직을 수정하여 PersonCorporateContract 기반으로 approved 직원을 조회하도록 변경합니다.

시드데이터의 무결성을 검증하고 시드데이터를 보완하여라.
그리고 시드데이터가 잘못된 것으로 계속 로직이 바뀌는 것을 검토하고 문제를 보고하여라.
일반적 개발로직을 서칭하여 비교하여라. 
이전 작업도 employee_number 고려되어야 하는지에 대하여 검토하고. 이에 대하여 정상적 범주내에서 과도한 수정인지 보고하여라.
근본적인 해결책을 제안하여라.

계약목록, 계정관리, 직원목록을 비교하여 버그 체크를 하여려 논리적 프로세스와 로직을 검토 비교하여 분석해 보고하여라.


employee_id는 왜 제거 되었으며 db 는 어떻게 관리되는가 
employee_id가 제거 되면 안되는거 아닌가가

현재 아이디의 규정이 없다. 아이디와 이메일, 비밀번호를 일치하는 방안과 일반적인  





기능적으로 필터만 제어하는 파일이나 기능은 없는가?
왜 재직의 상태가 두개로 나오는가 


 핵심 질문 답변 요약

 Q1: 직원목록에 퇴사/기준없이 노출되는 문제

 현상: 직원목록이 계약 완료된 직원만 표시해야 하는데 퇴사 직원도 노출됨

 원인 분석:
 - 21번 원칙: PCC.status='approved' 필터만 적용 (list_routes.py:82-121)
 - 퇴사 필터 누락: resignation_date 체크하는 로직 없음
 - 퇴사 직원도 계약이 approved면 그대로 표시됨

 해결 방안: resignation_date 필터 추가 필요

 ---
 Q2: "재직" vs "정상"의 차이

 | 용어     | 의미                           | 위치                         |
 |----------|--------------------------------|------------------------------|
 | 재직상태 | Employee.status 필드의 UI 라벨 | 소속정보 섹션                |
 | 정상     | status='active'의 한글 라벨    | FieldOptions.EMPLOYEE_STATUS |

 결론: "재직상태"는 필드명, "정상"은 값의 라벨. 둘은 동일한 것을 가리킴.

 ---
 Q3: 각 상태 뱃지의 의미

 Employee.status 뱃지 (field_options.py:62-68):
 | 값               | 라벨         | 뱃지색상               |
 |------------------|--------------|------------------------|
 | active           | 정상         | 초록 (badge-success)   |
 | pending_info     | 정보입력대기 | 회색 (badge-secondary) |
 | pending_contract | 계약대기     | 회색 (badge-secondary) |
 | warning          | 대기         | 주황 (badge-warning)   |
 | expired          | 만료         | 빨강 (badge-danger)    |

 PersonCorporateContract.status 뱃지 (field_options.py:102-109):
 | 값         | 라벨       | 뱃지색상               |
 |------------|------------|------------------------|
 | requested  | 계약진행중 | 주황 (badge-warning)   |
 | approved   | 계약완료   | 초록 (badge-success)   |
 | rejected   | 거절됨     | 빨강 (badge-danger)    |
 | terminated | 종료됨     | 회색 (badge-secondary) |
 | expired    | 만료됨     | 회색 (badge-secondary) |


 Q4: "정규직" vs "regular"의 차이

 동일한 것:
 - regular = DB 저장값 (영문)
 - 정규직 = UI 표시값 (한글 라벨)

 정의 위치 (field_options.py:87-92, 95-100):
 EMPLOYMENT_TYPE = [Option('regular', '정규직'), ...]  # Employee.contract.employee_type
 CONTRACT_TYPE = [Option('employment', '정규직'), ...] # PersonCorporateContract.contract_type

 주의: 두 옵션 세트가 다름
 - EMPLOYMENT_TYPE: Employee의 고용형태 (regular, contract, parttime, intern)
 - CONTRACT_TYPE: 계약 유형 (employment, contract, freelance, intern)

 ---
 Q5: 계약목록의 부서/직위 미출력 원인

 코드 분석 결과: 출력 로직은 정상

 - PersonCorporateContract 모델: department, position 필드 존재 (person_contract.py:55-56)
 - 템플릿 출력: {{ contract.department or '-' }} (macros/_contracts.html:362-363)
 - 데이터 전달: to_dict(include_relations=True)로 포함됨

 추정 원인:
 1. 데이터 미입력: 계약 생성 시 department/position 입력하지 않음
 2. Employee vs Contract 분리: 직원목록은 Employee.department, 계약목록은 PCC.department 사용
 3. DB 확인 필요: person_corporate_contracts 테이블의 실제 데이터 확인 권장

 ---
 발견된 버그 목록

 BUG-2: 직원목록에 퇴사 직원 노출 (신규 발견)

 파일: app/blueprints/employees/list_routes.py (라인 82-121)

 현상: 퇴사 직원(resignation_date 있음)도 계약이 approved면 목록에 표시됨

 수정 방안:
 # 라인 121 전에 추가
 if emp_dict.get('resignation_date'):
     continue  # 퇴사 직원 스킵




> /sc:analyze --seq --ultrathink --depth-deep @agent-backend-architect @agent-python-expert @agent-Explore \
q1. 기존에는 필터가 되어 걸러졌는데 왜 걸러지지 않는가? 코드가 변경되었나.
그리고 계약 조건이 employee 는 acvive, 개인은 approved 로 되어 있는데 이전에 이것을 코드를 통해 용어는 변경하지 않고 조건을 통해 appoved로 변경하였다. 검토하여라.
차가로 각계정의 조건으리 파악하여 통합된 필터 로직이 없는가? 이것이 제일 큰 문제인것 같다. 그리고 조건의 변수 명이 다른이유도 있고
q2. 리스트에 동일한 재직상태인데 정상과 재직 두개로 나오는 오류는 왜 그런가? 동일한 계정인데 로직의 오류를 검토하여라.
q3. q1에서 언급한 바데로 개인과 직원 계정의 값이 틀리다. 두 계정의 차이점의 특성과 프로세스틑 거의 90%이상 동일하며, 
틀린점은 개인이 따로 독립된 계정이 있어 법인과 계약을 바로 맺는  것이고, 직원은 그 개인계정이 없어, 우선적으로 회사에서 관리자가 하위계정을 생성하여 주는것이다. 이에 계정으로 접속하여 프로필정보를        
입력하고 추가적인 계약을 통하는 것은 모두 동일하다. 
q4. 지금까언급한것과 같이 해당 내용도 계정만 다를 뿐이지 처리되는것은 동일해야하는데 구분을 지워놓아서 이러한 문제점이 생긴것이다. 
q5. 동일하며, 조건에 대한 것이 명확히 분리되지 않아서 이며, 두계정에서 하나로 처리되는 통합된 로직으로 변경 검토해야 할 것이다. 

현재 통합되지 않는것과 통합된것을 세부적으로 검토하여라. 현재 템플릿도 거의 조건상 두계정이 동일한 부분이 90% 이상인데 개인과 직원으로 나누어져 관리되고 있다. 
모두 포괄해서 순차적으로 검토하여라.







      Option('resigned', '퇴사'),  # 추가 terminated 계약종료 및 해지 와 