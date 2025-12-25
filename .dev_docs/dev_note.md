
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


      --
  Q1: 필터가 왜 걸러지지 않는가?

  분석 결과: 코드는 의도대로 작동하고 있습니다.

  | 계정 타입    | 현재 필터 조건                                | 위치                    |
  |--------------|-----------------------------------------------|-------------------------|
  | employee_sub | Contract.status == 'approved'                 | list_routes.py:101      |
  | personal     | Contract.status in ['approved', 'terminated'] | personal_service.py:406 |

  문제점: 통합된 필터 로직이 없어서 두 조건이 분리 관리됨

  변수명 차이 원인:
  - Employee.status: 직원 재직 상태 (active, pending_info 등) - 현재 미사용
  - Contract.status: 계약 승인 상태 (approved, requested 등) - 실제 필터에 사용

  ---
  Q2: "정상" vs "재직" 이중 표시 원인

  근본 원인: DB에 두 가지 값이 혼재되어 있음

  | DB 저장값 | FieldOptions 매칭 | 표시 라벨              |
  |-----------|-------------------|------------------------|
  | 'active'  | 매칭 성공         | '정상'                 |
  | '재직'    | 매칭 실패         | '재직' (원본값 그대로) |

  문제 파일들:
  - scripts/generate_sample_employees.py:241 - status='재직'
  - scripts/link_employee_user.py:184 - status='재직'
  - tests/conftest.py:123 - status='재직'
  - app/repositories/employee_repository.py:269 - status='퇴사'

  LEGACY_MAP 부재: '재직' → 'active' 변환 규칙이 없음

  ---
  Q3-Q5: 통합 현황 분석

  통합되어 있는 코드 (90%)

  | 계층       | 상태      | 비고                               |
  |------------|-----------|------------------------------------|
  | Repository | 완전 통합 | BaseRelationRepository 상속        |
  | Models     | 완전 통합 | Profile, Education 등 공유         |
  | Templates  | 완전 통합 | partials/employee_form/*.html 공유 |

  분리되어 중복된 코드 (문제)

  | 계층      | Personal            | Employee            | 유사도 |
  |-----------|---------------------|---------------------|--------|
  | Service   | personal_service.py | employee_service.py | 95%    |
  | Blueprint | personal.py         | employees/*.py      | 85%    |
  | 파일처리  | personal.py:20-45   | employees/files.py  | 90%    |

  핵심 문제

  현재 구조:
  personal.py → personal_service.py → profile_repository.py
  employees/  → employee_service.py → employee_repository.py
                   ↑
              (조건 불일치 발생)

  권장 구조:
  personal.py ─┐
               ├→ profile_relation_service.py → 공통 repository
  employees/  ─┘

  ---
  발견된 버그 및 수정 방안

  | 우선순위 | 버그               | 수정 방안                            |
  |----------|--------------------|--------------------------------------|
  | P0       | 재직상태 이중 표시 | LEGACY_MAP에 '재직': 'active' 추가   |
  | P1       | 통합 필터 부재     | 공통 계약 필터 메서드 생성           |
  | P2       | Service 이중화     | ProfileRelationService 생성으로 통합 |
  | P3       | Blueprint 중복     | app/blueprints/profiles/ 생성        |

  ---
  즉시 수정 필요 파일

  app/constants/field_options.py
  ├─ LEGACY_MAP에 '재직': 'active' 추가
  └─ EMPLOYEE_STATUS에 'resigned' 추가

  app/services/contract_service.py (또는 신규)
  └─ get_filtered_contracts() 통합 메서드 생성

  DB 마이그레이션
  └─ UPDATE employees SET status = 'active' WHERE status = '재직'

  ---
  수정을 진행하시겠습니까?  








  1. 직원목록 필터 조건

  조건: PCC.status="approved" AND PCC.employee_number = Employee.employee_number
        AND Employee.resignation_date IS NULL

  | No   | employee_number | 이름         | status       | 퇴사일 | PCC상태  | 직원목록   |
  |------|-----------------|--------------|--------------|--------|----------|------------|
  | 1    | EMP-2015-0003   | 서현우       | resigned     | -      | approved | O          |
  | 2    | EMP-2015-0004   | 류예린       | resigned     | O      | approved | X (퇴사)   |
  | 3    | EMP-2015-0005   | 이시연       | active       | -      | approved | O          |
  | 4    | EMP-2015-0007   | 최유리       | active       | -      | approved | O          |
  | 5    | EMP-2015-0008   | 정민영       | active       | -      | approved | O          |
  | 6    | EMP-2015-0010   | 박지현       | active       | -      | approved | O          |
  | 7~36 | EMP-2015-* ~    | (30명)       | active       | -      | -        | X (미계약) |
  | 37   | EMP-2019-0002   | 정우성       | active       | -      | approved | O          |
  | 38   | EMP-2019-0006   | 권지훈       | active       | -      | approved | O          |
  | 41   | EMP-2020-0009   | 송유진       | active       | -      | approved | O          |
  | 48   | EMP-2024-0001   | 임영호       | resigned     | -      | approved | O          |
  | 51   | EMP-2025-0052   | 테스트직원2  | pending_info | -      | approved | O          |
  | 52   | EMP-2025-0053   | 상진환       | active       | -      | approved | O          |
  | 53   | EMP-2025-0054   | 박지우       | resigned     | O      | -        | X (퇴사)   |
  | 54   | EMP-2025-0055   | 이서준       | resigned     | O      | approved | X (퇴사)   |
  | 55   | EMP-2025-0056   | 김준혁       | active       | -      | approved | O          |
  | 57   | EMP-2025-0058   | 테스트직원02 | pending_info | -      | approved | O          |
  | 58   | EMP-2025-0058-1 | 이종선       | pending_info | -      | approved | O          |
  | 60   | EMP-2025-0064   | 롤백테스트   | pending_info | -      | approved | O          |

  요약: 총 60명 중 15명 표시 (퇴사 4명 제외, 미계약 41명 제외)

직원목록 목 첫번째는 pcc가 approved 된 상태이며, pending_info 상태는 미계약 상태이기 때문에 해당되지 않는다. > 계약목록에 유지
resigned, approved 는 퇴사한 상태이며, 퇴사일이 있어야 정상이고 직원목록에서 제외된다.
직원목록 조건은 acvive, approved 이다. 
pcc 상태개 비워져 있는 것은 무엇인가? 계약이 되지 않은 상태 외에 미계약, 계약해지로 할 수 있으며, 
계약 해지의 경우 resigned, approved 조건에 해당되기 때문에 적합한 용어를 추가해야한다. > resigned + terminated
그리고 제일 처음 언급한 pending_info 와 approved는 공존할 수 없다. pending_info는 계약전이기 때문이다.

데이터 정합성 검증: pending_info + approved 조합 데이터 수정 필요
퇴사일 필수화: resigned 상태는 반드시 resignation_date 필요
계약 상태 명확화: NULL vs 'terminated' vs 'rejected' 구분 필요

pending_info는 Employee 상태이고, PCC 상태와는 별개입니다. pending_info + approved 조합은 "직원 정보는 미완성이지만 계약은 승인됨"을 의미하므로 데이터 정합성 검증이 필요
>> 계약 승인 시점(PersonCorporateContract.status → approved)에 자동으로 Employee.status를 pending_info → active로 변경 결론 active , approved 전환

requested → approved (승인)
         → rejected (거절)
         → terminated (종료)

   | resigned       | approved   | 있음             | X        | O        | 정상 퇴사 |
   | resigned       | terminated | 있음             | X        | O        | 계약 종료 후 퇴사 |
    공존 불가
         
resigned 시 apprved >> terminated 변경 



  ---
  2. 계약목록 필터 조건

  조건: PCC.company_id = 1

  | No  | PCC_ID | employee_number | status     | User Email                     | Employee         |
  |-----|--------|-----------------|------------|--------------------------------|------------------|
  | 1   | 38     | NULL            | terminated | jung518@testcorp.co.kr         | X                |
  | 2   | 39     | NULL            | terminated | seo623@testcorp.co.kr          | X                |
  | 3   | 40     | NULL            | terminated | shin49@testcorp.co.kr          | X                |
  | 4   | 41     | EMP-2015-0005   | approved   | lee597@testcorp.co.kr          | O (이시연)       |
  | 5   | 42     | EMP-2019-0006   | approved   | kwon413@testcorp.co.kr         | O (권지훈)       |
  | 6   | 43     | EMP-2015-0007   | approved   | choi996@testcorp.co.kr         | O (최유리)       |
  | 7   | 44     | EMP-2015-0008   | approved   | jung330@testcorp.co.kr         | O (정민영)       |
  | 8   | 45     | EMP-2020-0009   | approved   | song653@testcorp.co.kr         | O (송유진)       |
  | 9   | 46     | NULL            | terminated | park697@testcorp.co.kr         | X                |
  | 10  | 87     | NULL            | terminated | lim397@testcorp.co.kr          | X                |
  | 11  | 88     | EMP-2025-0054   | terminated | junhyuk.kim@gmail.com          | O (박지우)       |
  | 12  | 89     | EMP-2025-0055   | terminated | seojun.lee@gmail.com           | O (이서준)       |
  | 13  | 90     | NULL            | rejected   | jiwoo.lee@gmail.com            | X                |
  | 14  | 91     | NULL            | requested  | test_provision2@test.com       | X                |
  | 15  | 92     | NULL            | terminated | junhyuk.kim@gmail.com          | X                |
  | 16  | 94     | EMP-2025-0056   | approved   | junhyuk.kim@gmail.com          | O (김준혁)       |
  | 17  | 95     | EMP-2015-0003   | approved   | seo623@testcorp.co.kr          | O (서현우)       |
  | 18  | 96     | EMP-2015-0004   | approved   | shin49@testcorp.co.kr          | O (류예린)       |
  | 19  | 97     | EMP-2025-0058-1 | approved   | jongsun@naver.com              | O (이종선)       |
  | 20  | 99     | EMP-2019-0002   | approved   | jung518@testcorp.co.kr         | O (정우성)       |
  | 21  | 100    | EMP-2025-0052   | approved   | test_provision2@test.com       | O (테스트직원2)  |
  | 22  | 101    | EMP-2024-0001   | approved   | lim397@testcorp.co.kr          | O (임영호)       |
  | 23  | 102    | EMP-2025-0053   | approved   | sangjeans@gmail.com            | O (상진환)       |
  | 24  | 103    | EMP-2015-0010   | approved   | park697@testcorp.co.kr         | O (박지현)       |
  | 25  | 104    | EMP-2025-0055   | approved   | seojun.lee@gmail.com           | O (이서준)       |
  | 26  | 105    | NULL            | approved   | testuser456@test.com           | X (문제)         |
  | 27  | 106    | EMP-2025-0058   | approved   | testprovision02@testcorp.co.kr | O (테스트직원02) |
  | 28  | 107    | EMP-2025-0064   | approved   | rollbacktest@testcorp.co.kr    | O (롤백테스트)   |

  요약: 총 28건 (approved 18건, terminated 7건, rejected 1건, requested 1건)

  사원번호(employee_number) 관리 원칙:
  - 계약 승인(approved) 시점에 영구 부여
  - 한 번 부여된 사원번호는 재사용 불가 (terminated/rejected 후에도 유지)
  - NULL 상태는 requested 단계에서만 허용
  - approved 상태에서 NULL은 데이터 무결성 위반 (PCC#105 수정 필요)


네, 맞습니다. 계약 목록은 모든 계약 상태(approved, terminated, rejected, requested)를 포함해야 합니다.
이유:
계약 이력 관리: 종료(terminated)되거나 거절(rejected)된 계약도 이력으로 보관해야 합니다
현재 데이터 구조: 선택된 표에서 이미 28건 전체(approved 18건, terminated 7건, rejected 1건, requested 1건)를 보여주고 있습니다
직원 목록과의 차이: 직원 목록은 approved + active + 미퇴사 조건으로 필터링하지만, 계약 목록은 company_id만으로 필터링하여 모든 계약 이력을 표시합니다
다만, ContractFilterService의 ACTIVE_STATUSES = ['approved', 'terminated']는 활성 계약만 조회하는 용도이므로, 계약 목록 페이지에서는 이 필터를 사용하지 않고 전체 조회해야 합니다.



  요약: 총 28건 (approved 18건, terminated 7건, rejected 1건, requested 1건)

  ---
  3. 계정관리 필터 조건

  조건: User.account_type="employee_sub" AND User.company_id=1

  | No  | User_ID | Email                          | employee_id | Employee        | 계약상태 |
  |-----|---------|--------------------------------|-------------|-----------------|----------|
  | 1   | 6       | lim397@testcorp.co.kr          | 1           | O (임영호)      | approved |
  | 2   | 7       | jung518@testcorp.co.kr         | 2           | O (정우성)      | approved |
  | 3   | 8       | seo623@testcorp.co.kr          | 3           | O (서현우)      | approved |
  | 4   | 9       | shin49@testcorp.co.kr          | 4           | O (류예린)      | approved |
  | 5   | 10      | lee597@testcorp.co.kr          | 5           | O (이시연)      | approved |
  | 6   | 11      | kwon413@testcorp.co.kr         | 6           | O (권지훈)      | approved |
  | 7   | 12      | choi996@testcorp.co.kr         | 7           | O (최유리)      | approved |
  | 8   | 13      | jung330@testcorp.co.kr         | 8           | O (정민영)      | approved |
  | 9   | 14      | song653@testcorp.co.kr         | 9           | O (송유진)      | approved |
  | 10  | 15      | park697@testcorp.co.kr         | 10          | O (박지현)      | approved |
  | 11  | 66      | test_provision2@test.com       | 52          | O (테스트직원2) | approved |
  | 12  | 67      | sangjeans@gmail.com            | 53          | O (상진환)      | approved |
  | 13  | 68      | jongsun@naver.com              | 58          | O (이종선)      | approved |
  | 14  | 69      | testuser456@test.com           | NULL        | X               | approved |
  | 15  | 70      | testprovision02@testcorp.co.kr | NULL        | X               | approved |
  | 16  | 71      | rollbacktest@testcorp.co.kr    | 64          | O (롤백테스트)  | approved |

  요약: 총 16명 (Employee 연결 14명, 미연결 2명)


  해당 계약 상태는 계정 생성과는 별개이다. 계약이 승인된 이후에 계약 상태가 결정되어진다. 해당 조건을 다시 체크하여라.
  

  --